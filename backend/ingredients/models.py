from django.db import models


class MeasurementUnit(models.Model):
    unit = models.CharField('Единица измерения', max_length=200)

    class Meta:
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'

    def __str__(self):
        return self.unit


class Ingredient(models.Model):
    measurement_unit = models.ForeignKey(
        MeasurementUnit,
        related_name='ingredient',
        on_delete=models.CASCADE,
        unique=False,
        verbose_name='Единица измерения',
    )
    name = models.CharField('Название', max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name
