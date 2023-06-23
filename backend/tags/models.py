from django.db import models


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=200,
        unique=True,
    )
    slug = models.SlugField(
        'Краткое название',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        'Цвет',
        max_length=7,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Бархатные Тяги'

    def __str__(self):
        return self.name


