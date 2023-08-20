from django.core.validators import (MaxValueValidator,
                                    MinValueValidator,
                                    RegexValidator
                                    )
from django.db import models

from recipes import constants
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Тег',
        max_length=constants.LENGTH_OF_FIELDS_RECIPES,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=constants.LENGTH_OF_FIELDS_RECIPES,
    )
    color = models.CharField(
        'HEX',
        max_length=7,
        null=True,
        validators=[
            RegexValidator(
                '^#([a-fA-F0-9]{6})',
                message='Поле должно содержать HEX-код.'
            )
        ]
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=constants.LENGTH_OF_FIELDS_RECIPES
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=constants.LENGTH_OF_FIELDS_RECIPES
    )

    class Meta():
        verbose_name = 'Ингридиенты'
        verbose_name_plural = 'Ингридиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipe'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингридиенты',
        through='IngredientInRecipe'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=constants.LENGTH_OF_FIELDS_RECIPES
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None,
        verbose_name='Изображение'
    )
    text = models.TextField('Описание')
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    cooking_time = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Время приготовления',
        validators=[MinValueValidator(
            1, message='Слишком быстро готовится.'
        ), MaxValueValidator(
            1500, message='Слишком долго готовить'
        )]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(
            1, message='Обратите внимание на количество'
        ), MaxValueValidator(
            5500, message='Слишком большое количество'
        )]
    )

    def __str__(self):
        return self.recipe.name

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'


class FavoriteShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',

    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_unique'
            )
        ]

    def __str__(self):
        return f'{self.user} :: {self.recipe}'


class Favorite(FavoriteShoppingCart):

    class Meta(FavoriteShoppingCart.Meta):
        default_related_name = 'favorite'
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Любимые рецепты'


class ShoppingCart(FavoriteShoppingCart):

    class Meta(FavoriteShoppingCart.Meta):
        default_related_name = 'shopping_carts'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
