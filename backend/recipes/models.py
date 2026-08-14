from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from .constants import (
    INGREDIENT_NAME_MAX_LENGTH, MEASUREMENT_UNIT_MAX_LENGTH,
    MIN_COOKING_TIME, MIN_INGREDIENT_AMOUNT, RECIPE_NAME_MAX_LENGTH,
    TAG_NAME_MAX_LENGTH, TAG_SLUG_MAX_LENGTH,
)


class Tag(models.Model):
    name = models.CharField(
        'Название', max_length=TAG_NAME_MAX_LENGTH, unique=True,
    )
    slug = models.SlugField(
        'Слаг', max_length=TAG_SLUG_MAX_LENGTH, unique=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название', max_length=INGREDIENT_NAME_MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        'Единица измерения', max_length=MEASUREMENT_UNIT_MAX_LENGTH,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient_measurement_unit',
            ),
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField('Название', max_length=RECIPE_NAME_MAX_LENGTH)
    image = models.ImageField('Картинка', upload_to='recipes/images/')
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag, related_name='recipes', verbose_name='Теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=[MinValueValidator(MIN_COOKING_TIME)],
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество', validators=[MinValueValidator(MIN_INGREDIENT_AMOUNT)],
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient',
            ),
        ]

    def __str__(self):
        return f'{self.ingredient} в «{self.recipe}»'


class UserRecipeRelation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_%(class)s',
            ),
        ]

    def __str__(self):
        return f'{self.recipe} — {self.user}'


class Favorite(UserRecipeRelation):

    class Meta(UserRecipeRelation.Meta):
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'Избранное'


class ShoppingCart(UserRecipeRelation):

    class Meta(UserRecipeRelation.Meta):
        verbose_name = 'рецепт в списке покупок'
        verbose_name_plural = 'Список покупок'
