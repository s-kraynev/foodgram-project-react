from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from api.common.filters import RecipeFilter
from api.common.mixins import DenyPutViewSet
from api.common.serializers import ShortRecipeSerializer
from api.common.utils import generate_pdf_file
from recipes.models import Favorite, Recipe, ShoppingCart, UsedIngredient
from .serializers import (
    FavoriteSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
)

User = get_user_model()


class RecipeViewSet(DenyPutViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeWriteSerializer
        elif self.action in ('list', 'retrieve'):
            return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_recipe(self):
        return get_object_or_404(Recipe, id=self.kwargs.get('pk'))

    @action(
        methods=['POST'],
        detail=True,
    )
    def favorite(self, request, **kwargs):
        user = request.user
        input_serializer = FavoriteSerializer(
            user, data=request.data, context={'request': request}
        )
        input_serializer.is_valid(raise_exception=True)
        recipe = self.get_recipe()
        output_serializer = ShortRecipeSerializer(
            recipe, context={'request': request}
        )
        output_serializer.validate({'favorite'})
        Favorite.objects.create(user=user, recipe=recipe)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @favorite.mapping.delete
    def delete_favorite(self, request, **kwargs):
        user = request.user
        serializer = FavoriteSerializer(
            user, data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        recipe = self.get_recipe()
        output_serializer = ShortRecipeSerializer(
            recipe, context={'request': request}
        )
        output_serializer.validate({'favorite'})
        Favorite.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST'],
        detail=True,
    )
    def shopping_cart(self, request, **kwargs):
        user = request.user
        recipe = self.get_recipe()
        serializer = ShortRecipeSerializer(
            recipe, context={'request': request}
        )
        serializer.validate({'shopping'})
        ShoppingCart.objects.create(user=user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, **kwargs):
        user = request.user
        recipe = self.get_recipe()
        serializer = ShortRecipeSerializer(
            recipe, context={'request': request}
        )
        serializer.validate({'shopping'})
        ShoppingCart.objects.get(user=user, recipe=recipe).delete()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def download_ingredients(request):
    used_ingredients = UsedIngredient.objects.filter(
        recipe__shopping_recipe__user=request.user
    )
    result = used_ingredients.values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(
        name=F('ingredient__name'),
        measurement_unit=F('ingredient__measurement_unit'),
        amount=Sum('amount'),
    )
    output_text = []
    for res in result:
        output_text.append(
            f'{res["name"]} ({res["measurement_unit"]}) - {res["amount"]}'
        )
    result = generate_pdf_file(output_text)
    return FileResponse(
        result, as_attachment=True, filename='Список_покупок.pdf'
    )
