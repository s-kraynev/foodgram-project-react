from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
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
    # NOTE: redefine password, because it has custom length <=150
    # the default value is a <=128
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
                'Имя пользователя содержит недопустимый символ'
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
        # NOTE: looks like I was wrong about Follow class. I told about Users
        # part, but the Follow I took from old work. However, it was also
        # reviewed it :)
        # https://github.com/s-kraynev/hw05_final/blob/master/yatube/posts/
        # models.py#L103
        # In group I found the right version, but this particular comment was
        # fixed not by me and I forgot about it after review in group project.
        # so it is my shame.
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'user',
                    'author',
                ),
                name='unique subscriber',
            ),
        )

    def __str__(self):
        return f'{self.user} подписан на пользователя: {self.author}'
