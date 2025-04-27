from django.contrib.auth import authenticate, get_user_model
from drf_extra_fields.fields import Base64ImageField

from ingridients.models import Ingredient
from recipes.models import IngredientInRecipe, Recipe
from rest_framework import serializers
from tags.models import Tag
from users.models import Subscriptions

User = get_user_model()


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя."""
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ['avatar']


class EmailAuthSerializer(serializers.Serializer):
    """Сериализатор для аутентификации по email и паролю."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Проверяет учетные данные и аутентифицирует пользователя."""
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password
            )
            if not user:
                raise serializers.ValidationError(
                    "Невозможно войти с предоставленными учетными данными."
                )
        else:
            raise serializers.ValidationError(
                'Требуется указать "email" и "password".'
            )

        attrs['user'] = user
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """Сериализатор для изменения пароля пользователя."""
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        """Проверяет текущий пароль пользователя."""
        user = self.context['request'].user
        if not user.check_password(attrs['current_password']):
            raise serializers.ValidationError({
                "current_password": "Неверный текущий пароль"
            })
        return attrs


class CustomUserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации новых пользователей."""
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'password',
            'first_name',
            'last_name'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """Создает нового пользователя с хешированием пароля."""
        return User.objects.create_user(**validated_data)

    def validate(self, data):
        """Проверяет обязательное поля username."""
        if not data.get('username'):
            raise serializers.ValidationError(
                {"username": "Это поле обязательно."}
            )
        return data


class UserCreateResponseSerializer(serializers.ModelSerializer):
    """Сериализатор для ответа после успешной регистрации."""
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name']


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля пользователя с дополнительными полями."""
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed'
        )
        extra_kwargs = {
            'avatar': {'write_only': True}
        }

    def get_avatar(self, obj):
        """Возвращает абсолютный URL аватара пользователя."""
        if not obj.avatar:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.avatar.url)
        return obj.avatar.url

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на данного."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscriptions.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        return False


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
    author = UserProfileSerializer(read_only=True)
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
        return (
            user.is_authenticated
            and obj.favorites.filter(user=user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, добавлен ли рецепт в корзину."""
        user = self.context["request"].user
        return (
            user.is_authenticated
            and obj.shopping_cart.filter(user=user).exists()
        )


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

        validated_data.pop('author', None)

        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )

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
        """Возвращает URL аватара автора."""
        if obj.avatar:
            return obj.avatar.url
        return None
