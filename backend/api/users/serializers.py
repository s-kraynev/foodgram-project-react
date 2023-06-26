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

    # NOTE: looks like 'fields' and 'readonly_fields' should be displayed
    # together: https://docs.djangoproject.com/en/4.2/ref/contrib/admin/
    # #django.contrib.admin.ModelAdmin.readonly_fields
    # Note that when specifying ModelAdmin.fields or ModelAdmin.fieldsets
    # the read-only fields must be present to be shown
    # (they are ignored otherwise).
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

    def validate(self, attrs):
        method = self.context['request'].method
        user = self.context['request'].user
        author = self.instance
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться/отписаться на/от самого себя'
            )
        subscription_exist = Follow.objects.filter(
            user=user, author=author
        ).exists()
        if method == 'DELETE' and not subscription_exist:
            raise serializers.ValidationError(
                'Ошибка отписки: Вы не подписаны на этого автора.'
            )
        elif method == 'POST' and subscription_exist:
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора'
            )
        return attrs
