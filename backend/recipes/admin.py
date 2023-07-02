from collections import defaultdict

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import Q

from .models import Favorite, Recipe, ShoppingCart


class IngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [
        IngredientInline,
    ]
    exclude = ['ingredients']
    list_display = (
        'name',
        'author',
        'favorite_score',
    )
    search_fields = ('name',)
    filter_horizontal = ('tags',)
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'

    @admin.display(description='Добавлен в избранное (раз)')
    def favorite_score(self, obj):
        return obj.count_favorites()

    @staticmethod
    def _add_to_used_ingredients(used_ingredients, objects, with_nested=True):
        for used in objects:
            key = used.ingredient.name if with_nested else used.name
            used_ingredients[key] += 1

    def save_formset(self, request, form, formset, change):
        formset.save(commit=False)
        used_ingredients = defaultdict(int)
        self._add_to_used_ingredients(used_ingredients, formset.new_objects)
        if change:
            # drop removed objects from instance
            for obj in formset.deleted_objects:
                obj.delete()
            changed_ingredients = [
                obj[0] for obj in formset.changed_objects
            ]
            # add changed
            self._add_to_used_ingredients(
                used_ingredients, changed_ingredients
            )

            existing_ingredients = formset.instance.ingredients.filter(
                ~Q(used_ingredient__in=changed_ingredients)
            )
            # add existing and not changed
            self._add_to_used_ingredients(
                used_ingredients, existing_ingredients, with_nested=False
            )

        if len(used_ingredients) < 1:
            raise ValidationError(
                'Нельзя создать рецепт без ингредиентов.'
            )
        duplicate_ingredients = []
        for ingr, count in used_ingredients.items():
            if count > 1:
                duplicate_ingredients.append(ingr)

        if duplicate_ingredients:
            raise ValidationError(
                f'Найдены дублирующиеся ингредиенты: {duplicate_ingredients}, '
                'пожалуйста оставьте один ингредиент.'
            )

        super(RecipeAdmin, self).save_formset(request, form, formset, change)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
