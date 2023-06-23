import base64

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (
    Favorite,
    Follow,
    Ingredient,
    Recipe,
    ShoppingCart,
    UsedIngredient,
)
from tags.models import Tag

User = get_user_model()


class ValidateUserSerializer:
    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        if username and username.lower() == 'me':
            raise serializers.ValidationError(
                'Пользователь me не может быть создан и изменен'
            )
        if (
            User.objects.filter(username=username).exists()
            and not User.objects.filter(**attrs).exists()
        ):
            raise serializers.ValidationError('Пользователь уже существует')
        if (
            User.objects.filter(email=email).exists()
            and not User.objects.filter(**attrs).exists()
        ):
            raise serializers.ValidationError(
                'Пользователь с такой почтой уже существует'
            )
        return attrs


class UserSerializer(ValidateUserSerializer, serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
        )


# NOTE: this class is used in settings.py
class RegisterSerializer(ValidateUserSerializer, serializers.ModelSerializer):
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        required=True,
        max_length=settings.MID_SMALL_INT_LENGTH,
    )
    email = serializers.EmailField(
        max_length=settings.BIG_INT_LENGTH,
        required=True,
    )
    first_name = serializers.CharField(
        required=True,
        max_length=settings.MID_SMALL_INT_LENGTH,
    )
    last_name = serializers.CharField(
        max_length=settings.MID_SMALL_INT_LENGTH,
        required=True,
    )
    password = serializers.CharField(
        max_length=settings.MID_SMALL_INT_LENGTH,
        required=True,
        style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password')

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super(RegisterSerializer, self).create(validated_data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.StringRelatedField()

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


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
        return obj.ingredient.measurement_unit.unit


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format_, imgstr = data.split(';base64,')
            ext = format_.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class ReadRecipeSerializer(serializers.ModelSerializer):
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


class CreateUsedIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        required=True, queryset=Ingredient.objects.all()
    )

    class Meta:
        model = UsedIngredient
        fields = ('id', 'amount')


class WriteRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=False)
    tags = serializers.ListSerializer(
        required=True,
        child=serializers.PrimaryKeyRelatedField(
            required=True, queryset=Tag.objects.all()
        ),
    )
    ingredients = CreateUsedIngredientSerializer(many=True, required=True)

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


# fix delete
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


class SubscribeSerializer(UserSerializer):
    recipes = ShortRecipeSerializer(many=True, source='recipe', required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
        )
        read_only_fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
        )

    @staticmethod
    def check_on_subscribe(user, author):
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        if Follow.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора'
            )

    @staticmethod
    def check_on_unsubscribe(user, author):
        if not Follow.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                'Ошибка отписки: Вы не подписаны на этого автора.'
            )
