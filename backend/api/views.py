
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .mixins import (
    CreateDestroyListViewSet,
    ListRetrieveViewSet,
    DenyPutViewSet,
    DenyPutPatchViewSet,
)
from .permissions import (
    IsAdmin,
    IsAdminAuthorOrReadOnly,
    IsAdminOrReadOnly,
)
from .serializers import (
    FollowSerializer,
    UserSerializer,
    IngredientSerializer,
    ReadRecipeSerializer,
    WriteRecipeSerializer,
    TagSerializer,
)
from recipes.models import Ingredient, Tag, Recipe, Follow

User = get_user_model()


class TagsViewSet(ListRetrieveViewSet):
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Tag.objects.all()
    pagination_class = None


class RecipeViewSet(DenyPutViewSet):
    queryset = Recipe.objects.all()
    #permission_classes = (permissions.Is,)

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


class IngredientViewSet(ListRetrieveViewSet):
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Ingredient.objects.all()
    pagination_class = None
    # TODO: не работает с русскими символами
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class SubscriptionViewSet(CreateDestroyListViewSet):
    serializer_class = FollowSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Follow.objects.all()


