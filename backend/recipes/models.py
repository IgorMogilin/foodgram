import random
import string

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from api.constants import (
    MINIMAL_COOCKING_TIME,
    RANDOM_STRING_LENGTH,
    RECIPE_MAX_LENGTH_NAME,
    RELATION_TYPE_MAX_LENGTH,
    SHORT_LINK_MAX_LENGTH
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
        blank=True,
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
        """Генерация случайной строки для короткой ссылки."""
        while True:
            short_link = ''.join(
                random.choices(
                    string.ascii_letters + string.digits,
                    k=RANDOM_STRING_LENGTH
                )
            )
            if not Recipe.objects.filter(short_link=short_link).exists():
                break
        return short_link

    def save(self, *args, **kwargs):
        """Переопределение метода save для генерации короткой ссылки."""
        if not self.short_link:
            self.short_link = self.generate_short_link()
        super().save(*args, **kwargs)

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
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField()

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
    FAVORITE = 'favorite'
    CART = 'cart'
    RELATION_CHOICES = [
        (FAVORITE, 'Избранное'),
        (CART, 'Корзина'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipe_relations'
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='user_relations'
    )
    relation_type = models.CharField(
        max_length=RELATION_TYPE_MAX_LENGTH,
        choices=RELATION_CHOICES
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe', 'relation_type'],
                name='unique_user_recipe_relation'
            )
        ]
        verbose_name = 'Связь пользователя с рецептом'
        verbose_name_plural = 'Связи пользователей с рецептами'
