from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, GenericViewSet

from .filters import IngredientFilter, RecipeFilter
from .mixins import (
    ListViewSet,
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
    UserSerializer,
    IngredientSerializer,
    ReadRecipeSerializer,
    WriteRecipeSerializer,
    ShortRecipeSerializer,
    SubscribeSerializer,
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


class SubscribeViewSet(ViewSet):
    queryset = Follow.objects.all()

    def get_author(self):
        return get_object_or_404(User, id=self.kwargs.get('id'))

    @action(
        methods=['POST'],
        detail=False,
        url_path='subscribe',
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author = self.get_author()
        # pass context for correct work is_subscribed in User serializator
        serializer = SubscribeSerializer(
            author, data=request.data, context={'request': request}
        )
        serializer.is_valid()
        serializer.check_on_subscribe(user, author)
        Follow.objects.create(user=user, author=author)
        # sorting number of recipes
        recipes_limit = request.query_params.get('recipes_limit')
        display_data = []
        iteration_data = serializer.data
        if isinstance(iteration_data, dict):
            iteration_data = [iteration_data]

        for author in iteration_data:
            display_data.append(author.copy())
            if recipes_limit is not None:
                display_data[-1]['recipes'] = (
                    display_data[-1]['recipes'][:int(recipes_limit)]
                )
        return Response(display_data, status=status.HTTP_200_OK)

    @subscribe.mapping.delete
    def unsubscribe(self, request, **kwargs):
        user = request.user
        author = self.get_author()
        # pass context for correct work is_subscribed in User serializator
        serializer = SubscribeSerializer(
            author, data=request.data, context={'request': request}
        )
        serializer.is_valid()
        subscription = Follow.objects.get(user=user, author=author)
        serializer.check_on_unsubscribe(subscription)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsViewSet(ListViewSet):
    queryset = Follow.objects.all()
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        authors = Follow.objects.filter(
            user=request.user).values_list('author', flat=True)
        queryset = User.objects.filter(id__in=authors).all()
        page = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            page, many=True, context={'request': request})
        # sorting number of recipes
        recipes_limit = request.query_params.get('recipes_limit')
        display_data = []
        for author in serializer.data:
            display_data.append(author.copy())
            if recipes_limit is not None:
                display_data[-1]['recipes'] = (
                    display_data[-1]['recipes'][:int(recipes_limit)]
                )
        return self.get_paginated_response(display_data)
