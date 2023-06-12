import base64
import datetime as dt

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (
    Favorite, Follow, Ingredient, MeasurementUnit, Recipe,
    ShoppingCart, Tag
)

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
        #TODO: fix it
        return Follow.objects.filter(author=obj).exists()

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
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'password'
        )

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super(RegisterSerializer, self).create(validated_data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'color', 'slug'
        )

    def create(self, validated_data):
        # TODO: change parsing color schema
        return Tag.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.color = validated_data.get('color', instance.color)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.save()
        return instance


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )
        read_only_fields = (
            'author',
        )

    def get_is_favorited(self, obj):
        return Favorite.objects.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        return ShoppingCart.objects.filter(recipe=obj).exists()

    def create(self, validated_data):
        # TODO: change parsing color schema
        return Tag.objects.create(**validated_data)

    def update(self, instance, validated_data):

        instance.save()
        return instance


class MeasurementUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementUnit
        fields = (
            'unit',
        )


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = MeasurementUnitSerializer(required=True)

    class Meta:
        model = Ingredient
        fields = (
            'id', 'name', 'measurement_unit',
        )


class FollowSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)
    author = UserSerializer(required=True)

    class Meta:
        model = Ingredient
        fields = (
            'id', 'user', 'author',
        )
