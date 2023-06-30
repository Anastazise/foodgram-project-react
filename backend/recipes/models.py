from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Tag(models.Model):
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    name = models.CharField('Название', unique=True, max_length=200)
    slug = models.SlugField('Слаг', unique=True, max_length=200)
    color = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=200)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    name = models.CharField('Название', max_length=200)
    author = models.ForeignKey(
        to=User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    text = models.TextField('Описание')
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(1, message='Минимальное значение 1')]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='Components',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )

    def __str__(self):
        return self.name


class Components(models.Model):
    class Meta:
        verbose_name = 'Компонент рецепта'
        verbose_name_plural = 'Компоненты рецепта'

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return (
            f'{self.ingredient.name} {self.amount}'
            f'({self.ingredient.measurement_unit})'
        )


class Favourite(models.Model):
    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'],
                             name='uniq_favourite')
        ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Избранное'


class Basket(models.Model):
    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'],
                             name='unique_basket')
        ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='basket',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='basket',
        verbose_name='Рецепт',
    )

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Корзину'
