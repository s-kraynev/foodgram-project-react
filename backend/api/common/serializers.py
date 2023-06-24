from rest_framework import serializers

from recipes.models import Recipe, ShoppingCart


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'cooking_time', 'image')
        model = Recipe

    @staticmethod
    def check_on_add_to_shopping_cart(user, recipe):
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в корзину покупок'
            )

    @staticmethod
    def check_on_remove_from_shopping_cart(user, recipe):
        if not ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError('Рецепта нет в корзине покупок')
