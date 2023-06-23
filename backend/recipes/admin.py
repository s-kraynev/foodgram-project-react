from django.contrib import admin

from .models import Favorite, Recipe, ShoppingCart


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'favorite_score',
    )
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'

    def favorite_score(self, obj):
        return obj.count_favorites()


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    pass


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    pass
