from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from ingredients.models import Ingredient
from tags.models import Tag

User = get_user_model()


class UsedIngredient(models.Model):
    amount = models.PositiveIntegerField(
        'Количество',
        validators=(MinValueValidator(1),),
        error_messages={'validators': 'Количество не может быть меньше 1!'},
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='used_ingredient',
        on_delete=models.CASCADE,
    )


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        related_name='recipe',
        on_delete=models.CASCADE,
    )
    name = models.CharField('Название', max_length=200)
    image = models.ImageField(
        'Картинка',
        upload_to='images/',
        null=True,
        default=None,
    )
    text = models.TextField('Описание')
    tags = models.ManyToManyField(Tag)
    cooking_time = models.IntegerField('Время готовки (минут)')
    ingredients = models.ManyToManyField(UsedIngredient)
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации', db_index=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('pub_date',)

    def __str__(self):
        return self.name

    @staticmethod
    def is_favorited(recipe, user):
        return Favorite.objects.filter(recipe=recipe, user=user).exists()

    @staticmethod
    def is_in_shopping_cart(recipe, user):
        return ShoppingCart.objects.filter(recipe=recipe, user=user).exists()

    def count_favorites(self):
        return Favorite.objects.filter(recipe=self).count()


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Рецепт в избpранном',
    )

    class Meta:
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Любимые рецепты'

    def __str__(self):
        return f'{self.recipe} в списке избранных рецептов у {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipe',
        verbose_name='Рецепт в корзине покупок',
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'

    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.user}'
