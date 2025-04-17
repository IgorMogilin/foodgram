from django.db import models
from django.core.validators import MinValueValidator
import shortuuid 
from users.models import User
from tags.models import Tag
from ingridients.models import Ingredient
from django.urls import reverse


class Recipe(models.Model):
    name = models.CharField(max_length=256)
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )
    image = models.ImageField(upload_to='recipes/', blank=True, default='')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',  # ← Это даст доступ через user.recipes.all()
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(Tag, related_name="recipes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
    
    def get_absolute_url(self):
        return reverse('recipe-detail', kwargs={'pk': self.pk})


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


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorites')  # важно!


class ShopingCart(models.Model):  # Лучше переименовать в ShoppingCart
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shopping_cart')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='shopping_cart') 


class ShortLink(models.Model):
    recipe = models.OneToOneField(
        'Recipe', 
        on_delete=models.CASCADE,
        related_name='short_link'
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        default=shortuuid.ShortUUID().random(3)
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} -> {self.recipe.name}"
