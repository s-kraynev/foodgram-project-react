from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.common.serializers import ShortRecipeSerializer
from users.models import Follow

User = get_user_model()


class ValidateUserSerializer:
    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        if username and username.lower() == 'me':
            raise serializers.ValidationError(
                'Пользователь me не может быть создан и изменен'
            )
        # NOTE: I took it from previous group project and forgot to remove.
        # thank you for reminder, that it is not relevant anymore
        if User.objects.filter(email=email).exists():
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
