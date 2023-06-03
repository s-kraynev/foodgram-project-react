from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    ROLES = (
        (USER, 'User'),
        (ADMIN, 'Admin'),
    )
    email = models.EmailField(
        blank=False,
        max_length=100,
        unique=True,
    )
    role = models.CharField(
        max_length=20,
        choices=ROLES,
        default=USER,
    )

    class Meta:
        # use ordering, because without we get warning in tests:
        # UnorderedObjectListWarning: Pagination may yield inconsistent
        # results with an unordered object_list
        ordering = ('id',)
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

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser
