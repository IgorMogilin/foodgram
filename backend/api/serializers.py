from django.contrib.auth import get_user_model

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from ingridients.models import Ingredient
from recipes.models import Favorite, IngredientInRecipe, Recipe, ShoppingCart
from tags.models import Tag
from users.models import Subscriptions

User = get_user_model()


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя."""

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class SubscriptionCreateSerializer(serializers.Serializer):
    """Сериализатор для создания подписки."""

    def validate(self, data):
        """Проверяет возможность создания подписки."""

        request = self.context['request']
        author = self.context['author']
        user = request.user

        if user == author:
            raise serializers.ValidationError(
                "Нельзя подписаться на самого себя."
            )
        if Subscriptions.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                "Вы уже подписаны на этого пользователя."
            )
        return data

    def create(self, validated_data):
        """Создает новую подписку пользователя на автора."""

        request = self.context['request']
        author = self.context['author']
        return Subscriptions.objects.create(user=request.user, author=author)


class SubscriptionDeleteValidator(serializers.Serializer):
    """Сериализатор для удаления подписки."""

    def validate(self, data):
        """Проверяет существование подписки для удаления."""

        request = self.context['request']
        author = self.context['author']
        if not Subscriptions.objects.filter(
            user=request.user,
            author=author
        ).exists():
            raise serializers.ValidationError(
                "Вы не подписаны на этого пользователя."
            )
        return data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на автора."""

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscriptions.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        return False

    def get_recipes(self, obj):
        """Возвращает список рецептов автора с возможностью ограничения."""

        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        recipes = obj.recipes.all()

        if limit:
            try:
                limit = int(limit)
                recipes = recipes[:limit] if limit > 0 else recipes.none()
            except (ValueError, TypeError):
                pass

        serializer = RecipeCustomSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Возвращает общее количество рецептов автора."""

        return obj.recipes.count()

    def get_avatar(self, obj):
        """Возвращает URL аватара автора с использованием AvatarSerializer."""

        avatar_serializer = AvatarSerializer(
            instance=obj, context=self.context
        )
        return avatar_serializer.data.get('avatar')


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя с флагом подписки и аватаром."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь."""

        request = self.context.get('request')
        return bool(
            request
            and request.user.is_authenticated
            and Subscriptions.objects.filter(
                user=request.user, author=obj
            ).exists()
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для связи ингредиентов и рецептов."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def validate_id(self, value):
        """Проверяет существование ингредиента."""

        if not Ingredient.objects.filter(id=value).exists():
            raise serializers.ValidationError("Ингредиент не существует")
        return value


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для детального отображения рецепта."""

    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        source="recipe_ingredients",
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time"
        ]

    def get_image(self, obj):
        """Возвращает абсолютный URL изображения рецепта."""

        if not obj.image:
            return ""
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

    def get_is_favorited(self, obj):
        """Проверяет, добавлен ли рецепт в избранное."""
        user = self.context["request"].user
        if not user.is_authenticated:
            return False
        return Favorite.objects.filter(
            user=user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, добавлен ли рецепт в корзину."""
        user = self.context["request"].user
        if not user.is_authenticated:
            return False
        return ShoppingCart.objects.filter(
            user=user,
            recipe=obj
        ).exists()


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""

    image = Base64ImageField(required=True)
    ingredients = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True
    )

    class Meta:
        model = Recipe
        fields = (
            "id", "ingredients", "tags", "image",
            "name", "text", "cooking_time"
        )
        read_only_fields = ("id", "author")

    def validate_ingredients(self, value):
        """Валидирует список ингредиентов."""

        if not value:
            raise serializers.ValidationError(
                "Необходимо указать хотя бы один ингредиент"
            )
        ingredient_ids = [item['id'] for item in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                "Ингредиенты не должны повторяться"
            )
        validated_ingredients = []
        for ingredient in value:
            if 'id' not in ingredient or 'amount' not in ingredient:
                raise serializers.ValidationError(
                    "Каждый ингредиент должен содержать id и amount"
                )
            try:
                ingredient_obj = Ingredient.objects.get(id=ingredient['id'])
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    f"Ингредиент с id {ingredient['id']} не существует"
                )
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError(
                    "Количество ингредиента должно быть больше 0"
                )
            validated_ingredients.append({
                'id': ingredient_obj.id,
                'amount': ingredient['amount']
            })
        return validated_ingredients

    def validate(self, data):
        """Общая валидация данных рецепта."""

        if self.context['request'].method in ['PUT', 'PATCH']:
            if 'ingredients' not in data:
                raise serializers.ValidationError({
                    'ingredients': 'Это поле обязательно при обновлении'
                })
        if 'tags' not in data or not data['tags']:
            raise serializers.ValidationError(
                {'tags': 'Необходимо указать хотя бы один тег'}
            )
        if len(data['tags']) != len(set(data['tags'])):
            raise serializers.ValidationError(
                {'tags': 'Теги не должны повторяться'}
            )
        if 'cooking_time' in data and data['cooking_time'] < 1:
            raise serializers.ValidationError(
                {'cooking_time': 'Время должно быть не менее 1 минуты'}
            )
        if 'image' not in data or not data['image']:
            raise serializers.ValidationError(
                {'image': 'Изображение обязательно'}
            )
        return data

    def create_ingredients(self, recipe, ingredients):
        """Создает связи между рецептом и ингредиентами."""

        IngredientInRecipe.objects.bulk_create([
            IngredientInRecipe(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ])

    def create(self, validated_data):
        """Создает новый рецепт."""

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        validated_data['author'] = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Обновляет существующий рецепт."""

        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)
        if ingredients is not None:
            instance.recipe_ingredients.all().delete()
            self.create_ingredients(instance, ingredients)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Возвращает сериализованные данные рецепта."""

        return RecipeSerializer(instance, context=self.context).data


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого отображения рецептов."""

    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        """Возвращает URL изображения рецепта."""

        if not obj.image:
            return ""
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class RecipeCustomSerializer(serializers.ModelSerializer):
    """Сериализатор для кастомного отображения рецептов."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class BaseUserRecipeRelationSerializer(serializers.ModelSerializer):

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = None
        fields = ('user', 'recipe')
        read_only_fields = ('user',)

    def validate(self, data):
        user = self.context['request'].user
        recipe = data['recipe']
        model = self.Meta.model
        if model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError("Рецепт уже добавлен.")
        return data

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(
            instance.recipe, context=self.context
        ).data


class FavoriteSerializer(BaseUserRecipeRelationSerializer):
    class Meta(BaseUserRecipeRelationSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(BaseUserRecipeRelationSerializer):
    class Meta(BaseUserRecipeRelationSerializer.Meta):
        model = ShoppingCart
