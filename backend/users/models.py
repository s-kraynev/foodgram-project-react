from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    first_name = models.CharField(
        max_length=settings.MID_SMALL_INT_LENGTH,

    )
    last_name = models.CharField(
        max_length=settings.MID_SMALL_INT_LENGTH,
    )
    email = models.EmailField(
        unique=True
    )
    password = models.CharField(
        max_length=settings.MID_SMALL_INT_LENGTH,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
