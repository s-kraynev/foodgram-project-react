from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from ingredients.models import Ingredient
from tags.models import Tag

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        related_name='recipe',
        on_delete=models.CASCADE,
    )
    # NOTE: I like django style too, but "black" util does not allow to split
    # on several lines short lines. Maybe it could be configured, but
    # I have not time to find such option for now. On team project I also
    # tried to find solution for such behaviour, but failed with it.
    name = models.CharField('Название', max_length=200)
    image = models.ImageField(
        'Картинка',
        upload_to='images/',
    )
    text = models.TextField('Описание')
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveIntegerField('Время готовки (минут)')
    ingredients = models.ManyToManyField(Ingredient, through='UsedIngredient')
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации', db_index=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

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
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return (
            f'Recipe {self.recipe} use {self.ingredient} '
            f'with amount {self.amount}'
        )


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
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'user',
                    'recipe',
                ),
                name='unique recipe in favorite',
            ),
        )

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
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'user',
                    'recipe',
                ),
                name='unique recipe in shopping cart',
            ),
        )

    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.user}'
