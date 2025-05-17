import base64
import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from api.constants import (
    MINIMAL_COOCKING_TIME,
    RECIPE_MAX_LENGTH_NAME,
    SHORT_LINK_MAX_LENGTH,
)
from ingridients.models import Ingredient
from tags.models import Tag
from users.models import User


class Recipe(models.Model):
    name = models.CharField(max_length=RECIPE_MAX_LENGTH_NAME)
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(MINIMAL_COOCKING_TIME)]
    )
    image = models.ImageField(
        upload_to='recipes/',
        blank=False,
        default="",
        null=False
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(Tag, related_name="recipes")
    created_at = models.DateTimeField(auto_now_add=True)

    short_link = models.CharField(
        max_length=SHORT_LINK_MAX_LENGTH,
        blank=True,
        null=True,
        verbose_name='Короткая ссылка'
    )

    def generate_short_link(self):
        uuid_bytes = uuid.uuid4().bytes
        short_link = base64.urlsafe_b64encode(
            uuid_bytes
        ).decode('utf-8').rstrip('=')
        return short_link[:SHORT_LINK_MAX_LENGTH]

    class Meta:
        """Мета-класс для настройки порядка и отображения рецептов."""
        ordering = ['-created_at']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        """Возвращает строковое представление рецепта."""
        return f"Рецепт: {self.name} (ID: {self.id})"


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингридиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe'
            )
        ]
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return f'{self.ingredient} — {self.amount} (для {self.recipe})'


class UserRecipeRelation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_%(class)s'
            )
        ]
        default_related_name = 'in_%(class)ss'


class Favorite(UserRecipeRelation):
    class Meta(UserRecipeRelation.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(UserRecipeRelation):
    class Meta(UserRecipeRelation.Meta):
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
