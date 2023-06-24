from django.contrib import admin

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
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'

    @admin.display(description='Добавлен в избранное (раз)')
    def favorite_score(self, obj):
        return obj.count_favorites()


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
