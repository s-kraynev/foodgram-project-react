from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from recipes.models import Recipe, ShoppingCart
from users.models import Follow

User = get_user_model()


# TODO move to common class later
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
