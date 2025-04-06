from rest_framework import serializers
from users.models import User
from tags.models import Tag
from ingridients.models import Ingredient
from recipes.models import Recipe, IngredientInRecipe


class TagSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = IngredientInRecipe
        fields = ['ingredient', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    tags = TagSerilizer(many=True)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        source="recipe_ingredients"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = [
            'id', 'author', 'name', 'image',
            'text', 'cooking_time', 'tags',
            'ingredients', 'is_favorited',
            'is_in_shoping_cart', 'created_at'
        ]
    
    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and obj.favorites.filter(user == user).exist
    
    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and obj.shopping_carts.filter(user == user).exist




