from django.shortcuts import get_object_or_404
from rest_framework import serializers

from api.common.serializer_fields import Base64ImageField
from api.tags.serializers import TagSerializer
from api.users.serializers import UserSerializer
from ingredients.models import Ingredient
from recipes.models import Favorite, Recipe, UsedIngredient
from tags.models import Tag


class UsedIngredientReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsedIngredient
        fields = ('id', 'amount', 'name', 'measurement_unit')

    def to_representation(self, instance):
        return {
            'id': instance.ingredient.id,
            'name': instance.ingredient.name,
            'measurement_unit': instance.ingredient.measurement_unit,
            'amount': instance.amount,
        }


class RecipeReadSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(required=True, many=True)
    ingredients = UsedIngredientReadSerializer(
        source='recipe', required=True, many=True
    )
    author = UserSerializer(required=True, many=False)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )
        read_only_fields = ('pub_date',)

    def get_is_favorited(self, obj):
        return Recipe.is_favorited(obj, self.context['request'].user.id)

    def get_is_in_shopping_cart(self, obj):
        return Recipe.is_in_shopping_cart(obj, self.context['request'].user.id)


class RecipeWriteSerializer(serializers.ModelSerializer):
    # NOTE: it was already allow_null=False on previous review too :)
    image = Base64ImageField(required=True, allow_null=False)
    tags = serializers.ListSerializer(
        required=True,
        child=serializers.PrimaryKeyRelatedField(
            required=True, queryset=Tag.objects.all()
        ),
    )
    ingredients = serializers.ListSerializer(
        child=serializers.JSONField(),
    )

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = (
            'author',
            'pub_date',
        )

    def validate_ingredients(self, value):
        unique_ingredients = []
        if len(value) < 0:
            raise serializers.ValidationError(
                'Нельзя создать рецепт без ингредиентов.'
            )
        for data_ingredient in value:
            ingredient = get_object_or_404(
                Ingredient, id=data_ingredient.get('id')
            )
            if ingredient in unique_ingredients:
                raise serializers.ValidationError(
                    f'Дублируется {ingredient.name}, пожалуйста оставьте один'
                    ' ингредиент.'
                )
            unique_ingredients.append(ingredient)
            if int(data_ingredient.get('amount')) < 0:
                raise serializers.ValidationError(
                    'Вы ввели некорректное значение ('
                    f'{data_ingredient.get("amount")}) для {ingredient.name}'
                )
        return value

    def to_representation(self, instance):
        serialized_ingredients = [
            {
                'id': ingredient.ingredient.id,
                'amount': ingredient.amount,
            }
            for ingredient in instance.recipe.all()
        ]
        serialized_data = super(RecipeWriteSerializer, self).to_representation(
            instance
        )
        serialized_data['ingredients'] = serialized_ingredients

        return serialized_data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            recipe.tags.add(tag)
        for ingredient in ingredients:
            db_ingredient = get_object_or_404(
                Ingredient, id=ingredient.get('id')
            )
            UsedIngredient.objects.create(
                **{
                    'recipe': recipe,
                    'amount': ingredient['amount'],
                    'ingredient': db_ingredient,
                }
            )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        instance.tags.set(tags)

        ingredients = validated_data.pop('ingredients')
        for ingr in instance.ingredients.all():
            used_ingr = UsedIngredient.objects.get(
                recipe=instance, ingredient=ingr
            )
            used_ingr.delete()
        for ingredient in ingredients:
            db_ingredient = get_object_or_404(
                Ingredient, id=ingredient.get('id')
            )
            UsedIngredient.objects.create(
                **{
                    'recipe': instance,
                    'amount': ingredient['amount'],
                    'ingredient': db_ingredient,
                }
            )

        return super(RecipeWriteSerializer, self).update(
            instance, validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_fields = ('id', 'recipe', 'user')
