from rest_framework import serializers

from recipes.models import Favorite, Recipe, ShoppingCart


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'cooking_time', 'image')
        model = Recipe

    def validate(self, attrs):
        method = self.context['request'].method
        user = self.context['request'].user
        recipe = self.instance
        if 'favorite' in attrs:
            favorite_exist = Favorite.objects.filter(
                user=user, recipe=recipe
            ).exists()
            if method == 'DELETE' and not favorite_exist:
                raise serializers.ValidationError(
                    'Рецепт не найден в избранных рецептах'
                )
            elif method == 'POST' and favorite_exist:
                raise serializers.ValidationError(
                    'Уже находится в избранных рецептах'
                )
        elif 'shopping' in attrs:
            shopping_exist = ShoppingCart.objects.filter(
                user=user, recipe=recipe
            ).exists()
            if method == 'DELETE' and not shopping_exist:
                raise serializers.ValidationError(
                    'Рецепта нет в корзине покупок'
                )
            elif method == 'POST' and shopping_exist:
                raise serializers.ValidationError(
                    'Рецепт уже добавлен в корзину покупок'
                )
        return attrs
