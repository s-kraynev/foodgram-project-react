
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.mixins import (
    ListRetrieveViewSet,
    DenyPutViewSet,
    DenyPutPatchViewSet,
)
from api.permissions import (
    IsAdmin,
    IsAdminAuthorOrReadOnly,
    IsAdminOrReadOnly,
)
from api.serializers import (
    RegisterSerializer,
    UserSerializer,
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer,
)
from recipes.models import Tag, Recipe

User = get_user_model()


class TagsViewSet(ListRetrieveViewSet):
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Tag.objects.all()


class RecipeViewSet(DenyPutViewSet):
    serializer_class = RecipeSerializer
    permission_classes = (IsAdminAuthorOrReadOnly,)
    queryset = Recipe.objects.all()
