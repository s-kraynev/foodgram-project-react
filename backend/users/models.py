from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


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
    # redefine password, because it has custom length <=150
    # the default value is a <=128
    password = models.CharField(
        max_length=settings.MID_SMALL_INT_LENGTH,
        verbose_name='Пароль',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


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
        unique_together = ['user', 'author']
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'

    def __str__(self):
        return f'{self.user} подписан на пользователя: {self.author}'
