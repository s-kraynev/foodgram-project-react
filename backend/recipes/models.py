from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        "Название",
        max_length=200,
        unique=True,
    )
    slug = models.SlugField(
        "Краткое название",
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        "Цвет",
        max_length=7,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Бархатные Тяги'

    def __str__(self):
        return self.name


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
    )
    name = models.CharField("Название", max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):

    author = models.ForeignKey(
        User,
        related_name='recipe',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        "Название",
        max_length=200
    )
    image = models.ImageField(
        "Картинка",
        upload_to='images/',
        null=True,
        default=None,
    )
    text = models.TextField("Описание")
    tags = models.ManyToManyField(
        Tag,
    )
    cooking_time = models.TimeField("Время готовки")
    ingredients = models.ManyToManyField(
        Ingredient,
        through="UsedIngredient"
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class UsedIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        related_name="used_ingredient",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="recipe",
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        "Количество",
        validators=(MinValueValidator(1),),
        error_messages={'validators': 'Количество не может быть меньше 1!'},
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        unique_together = ['user', 'author']
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'

    def __str__(self):
        return f'{self.user} follower of {self.author}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe'
    )

    class Meta:
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Любимые рецепты'

    def __str__(self):
        return f'{self.recipe} is favorite for {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipe'
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'

    def __str__(self):
        return f'{self.user} buy {self.recipe}'
