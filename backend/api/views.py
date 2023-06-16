from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .filters import IngredientFilter, RecipeFilter
from .mixins import (
    CreateDestroyListViewSet,
    ListRetrieveViewSet,
    DenyPutViewSet,
)
from .pagination import CustomPagination
from .permissions import (
    IsAdmin,
    IsAdminAuthorOrReadOnly,
    IsAdminOrReadOnly,
)
from .serializers import (
    FavoriteSerializer,
    FollowSerializer,
    UserSerializer,
    IngredientSerializer,
    ReadRecipeSerializer,
    WriteRecipeSerializer,
    ShortRecipeSerializer,
    TagSerializer,
)
from recipes.models import Ingredient, Tag, Recipe, Follow, Favorite

User = get_user_model()


class TagsViewSet(ListRetrieveViewSet):
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Tag.objects.all()
    pagination_class = None


class RecipeViewSet(DenyPutViewSet):
    # TODO: add order sorting by pub date
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return WriteRecipeSerializer
        elif self.action in ('list', 'retrieve'):
            return ReadRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FavoriteViewSet(ViewSet):
    queryset = Favorite.objects.all()

    def get_recipe(self):
        return get_object_or_404(Recipe, id=self.kwargs.get('id'))

    @action(
        methods=['POST'],
        detail=False,
        url_path='favorite',
    )
    def makes_favorite(self, request, **kwargs):
        user = request.user
        serializer = FavoriteSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = self.get_recipe()
        favorite_recipe = Favorite.objects.filter(user=user, recipe=recipe)
        serializer.check_recipe_add_favorite(favorite_recipe)
        Favorite.objects.create(user=user, recipe=recipe)
        return Response(
            ShortRecipeSerializer(recipe).data, status=status.HTTP_200_OK)

    @makes_favorite.mapping.delete
    def delete_favorite(self, request, **kwargs):
        user = request.user
        serializer = FavoriteSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = self.get_recipe()
        favorite_recipe = Favorite.objects.filter(user=user, recipe=recipe)
        serializer.check_recipe_del_favorite(favorite_recipe)
        favorite_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(ListRetrieveViewSet):
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Ingredient.objects.all()
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class SubscriptionViewSet(CreateDestroyListViewSet):
    serializer_class = FollowSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Follow.objects.all()


