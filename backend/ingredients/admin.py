from django.contrib import admin

from .models import Ingredient, MeasurementUnit


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(MeasurementUnit)
class MeasureUnitAdmin(admin.ModelAdmin):
    pass