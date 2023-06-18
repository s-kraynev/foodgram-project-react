from collections import defaultdict

from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from recipes.models import (
    Favorite,
    Follow,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
)

from .filters import IngredientFilter, RecipeFilter
from .mixins import DenyPutViewSet, ListRetrieveViewSet, ListViewSet
from .pagination import CustomPagination
from .serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    ReadRecipeSerializer,
    ShortRecipeSerializer,
    SubscribeSerializer,
    TagSerializer,
    WriteRecipeSerializer,
)
from .utils import generate_pdf_file

User = get_user_model()


class TagsViewSet(ListRetrieveViewSet):
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Tag.objects.all()
    pagination_class = None


class RecipeViewSet(DenyPutViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    filterset_class = RecipeFilter
    pagination_class = CustomPagination
    ordering = ('-pub_date',)

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
        serializer.check_recipe_add_favorite(user, recipe)
        Favorite.objects.create(user=user, recipe=recipe)
        return Response(
            ShortRecipeSerializer(recipe).data, status=status.HTTP_200_OK
        )

    @makes_favorite.mapping.delete
    def delete_favorite(self, request, **kwargs):
        user = request.user
        serializer = FavoriteSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = self.get_recipe()
        serializer.check_recipe_del_favorite(user, recipe)
        Favorite.objects.get(user=user, recipe=recipe).delete()
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
                display_data[-1]['recipes'] = display_data[-1]['recipes'][
                    : int(recipes_limit)
                ]
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
        serializer.check_on_unsubscribe(user, author)
        Follow.objects.get(user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsViewSet(ListViewSet):
    queryset = Follow.objects.all()
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        authors = Follow.objects.filter(user=request.user).values_list(
            'author', flat=True
        )
        queryset = User.objects.filter(id__in=authors).all()
        page = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            page, many=True, context={'request': request}
        )
        # sorting number of recipes
        recipes_limit = request.query_params.get('recipes_limit')
        display_data = []
        for author in serializer.data:
            display_data.append(author.copy())
            if recipes_limit is not None:
                display_data[-1]['recipes'] = display_data[-1]['recipes'][
                    : int(recipes_limit)
                ]
        return self.get_paginated_response(display_data)


class ShoppingCartViewSet(ViewSet):
    queryset = ShoppingCart.objects.all()

    def get_recipe(self):
        return get_object_or_404(Recipe, id=self.kwargs.get('id'))

    @action(
        methods=['POST'],
        detail=False,
        url_path='shopping_cart',
    )
    def add_to_shopping_cart(self, request, **kwargs):
        user = request.user
        recipe = self.get_recipe()
        serializer = ShortRecipeSerializer(recipe, data=request.data)
        serializer.is_valid()
        serializer.check_on_add_to_shopping_cart(user, recipe)
        ShoppingCart.objects.create(user=user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @add_to_shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, **kwargs):
        user = request.user
        recipe = self.get_recipe()
        serializer = ShortRecipeSerializer(recipe, data=request.data)
        serializer.is_valid()
        serializer.check_on_remove_from_shopping_cart(user, recipe)
        ShoppingCart.objects.get(user=user, recipe=recipe).delete()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def download_ingredients(request):
    shopping_records = ShoppingCart.objects.filter(user=request.user)
    ingredients_to_buy = defaultdict(int)
    # group ingredients by name
    for shopping_record in shopping_records:
        for ingredient in shopping_record.recipe.ingredients.all():
            key = (
                ingredient.ingredient.name,
                ingredient.ingredient.measurement_unit.unit,
            )
            ingredients_to_buy[key] += ingredient.amount
    # prepare final list of ingredients
    output_text = []
    for key, amount in ingredients_to_buy.items():
        output_text.append(f'{key[0]} ({key[1]}) - {amount}')
    result = generate_pdf_file(output_text)
    return FileResponse(
        result, as_attachment=True, filename='Список_покупок.pdf'
    )
