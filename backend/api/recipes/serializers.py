import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from api.tags.serializers import TagSerializer
from api.users.serializers import UserSerializer
from ingredients.models import Ingredient
from recipes.models import Favorite, Recipe, UsedIngredient
from tags.models import Tag


class UsedIngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    amount = serializers.IntegerField()

    class Meta:
        model = UsedIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format_, imgstr = data.split(';base64,')
            ext = format_.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeReadSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(required=True, many=True)
    ingredients = UsedIngredientSerializer(required=True, many=True)
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


class UsedIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        required=True, queryset=Ingredient.objects.all()
    )

    class Meta:
        model = UsedIngredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    # NOTE: it was already allow_null=False on previous review too :)
    image = Base64ImageField(required=True, allow_null=False)
    tags = serializers.ListSerializer(
        required=True,
        child=serializers.PrimaryKeyRelatedField(
            required=True, queryset=Tag.objects.all()
        ),
    )
    ingredients = UsedIngredientCreateSerializer(many=True, required=True)

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = (
            'author',
            'pub_date',
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            recipe.tags.add(tag)
        for ingredient in ingredients:
            ingredient['ingredient'] = ingredient.pop('id')
            used_ingredient = UsedIngredient.objects.create(**ingredient)
            recipe.ingredients.add(used_ingredient)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        tags = validated_data.pop('tags')
        instance.tags.set(tags)

        ingredients = validated_data.pop('ingredients')
        new_ingredients = []
        old_ingredients = list(instance.ingredients.all())
        for ingredient in ingredients:
            ingredient['ingredient'] = ingredient.pop('id')
            new_ingredients.append(UsedIngredient.objects.create(**ingredient))
        instance.ingredients.set(new_ingredients)

        for ingr in old_ingredients:
            ingr.delete()

        instance.save()
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_fields = ('id', 'recipe', 'user')

    @staticmethod
    def check_recipe_add_favorite(user, recipe):
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Уже находится в избранных рецептах'
            )

    @staticmethod
    def check_recipe_del_favorite(user, recipe):
        if not Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт не найден в избранных рецептах'
            )
