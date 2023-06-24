from django_filters.rest_framework import BooleanFilter, CharFilter, FilterSet

from recipes.models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(FilterSet):
    is_favorited = BooleanFilter()
    is_in_shopping_cart = BooleanFilter()
    tags = CharFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']

    def filter_queryset(self, queryset):
        # NOTE: behaviour with using is_in_shopping_cart and is_favorited
        # will return empty result (in case if recipe are not favorited and
        # is in shopping_cart). I think, that it's expected.
        # F.e. we could add page with only favorited recipes in shopping_cart.
        author = self.data.get('author')
        if author is not None:
            queryset = queryset.filter(author=author)

        is_favorited = self.data.get('is_favorited')
        if is_favorited is not None:
            queryset = queryset.filter(favorite_recipe__user=self.request.user)

        is_in_shopping_cart = self.data.get('is_in_shopping_cart')
        if is_in_shopping_cart is not None:
            queryset = queryset.filter(shopping_recipe__user=self.request.user)

        tags = self.data.get('tags')
        if tags is not None:
            # if tags are presented we have to get list if them instead of
            # the last one
            tags = self.data.getlist('tags')
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        return queryset
