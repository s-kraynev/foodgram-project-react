from django.db import models


class Ingredient(models.Model):
    measurement_unit = models.CharField('Единица измерения', max_length=200)
    name = models.CharField('Название', max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name
