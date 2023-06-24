from rest_framework import serializers

from ingredients.models import Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.StringRelatedField()

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )
