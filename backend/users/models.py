from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q


class User(AbstractUser):
    first_name = models.CharField(
        max_length=settings.MID_SMALL_INT_LENGTH,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=settings.MID_SMALL_INT_LENGTH,
        verbose_name='Фамилия',
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Почта',
    )
    password = models.CharField(
        max_length=settings.MID_SMALL_INT_LENGTH,
        verbose_name='Пароль',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def clean(self):
        super().clean()
        if self.username == 'me':
            raise ValidationError(
                'Имя пользователя "me" запрещено к использованию'
            )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор рецептов',
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'user',
                    'author',
                ),
                name='unique subscriber',
            ),
            # NOTE: This constraint is good, but it crushes admin page.
            # So I would leave clean method as well.
            models.CheckConstraint(
                name='author_is_not_the_same_user',
                check=~Q(user=F('author'))
            )
        )

    def __str__(self):
        return f'{self.user} подписан на пользователя: {self.author}'

    def clean(self):
        super().clean()
        if self.user == self.author:
            raise ValidationError('Нельзя подписаться на самого себя')
