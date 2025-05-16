from django.contrib import admin
from django.forms import ValidationError

from api.serializers import RecipeCreateUpdateSerializer
from recipes.models import Recipe, IngredientInRecipe


class IngredientInRecipeInline(admin.TabularInline):
    """
    Inline-форма для добавления ингредиентов к рецепту.
    """

    model = IngredientInRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Административная панель для модели Recipe.
    Позволяет управлять рецептами, отображать их список,
    искать по названию и автору, фильтровать по тегам,
    а также редактировать связанные ингредиенты через inline-форму.
    """

    list_display = ('name', 'author', 'favorites_count')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    inlines = [IngredientInRecipeInline]

    def favorites_count(self, obj):
        """
        Возвращает количество добавлений рецепта в избранное.
        """

        return obj.in_favorites.count()

    def save_model(self, request, obj, form, change):
        """
        Валидирует основные поля рецепта через сериализатор перед сохранением.
        В случае ошибок отображает понятное сообщение в админке.
        """

        data = {
            'name': form.cleaned_data.get('name'),
            'text': form.cleaned_data.get('text'),
            'cooking_time': form.cleaned_data.get('cooking_time'),
            'tags': form.cleaned_data.get('tags'),
        }
        serializer = RecipeCreateUpdateSerializer(
            data=data,
            context={'request': request}
        )
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            raise ValidationError(f"Ошибка валидации рецепта: {e}")
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        """
        Сохраняет связанные объекты автоматически через inline-формы.
        """

        super().save_related(request, form, formsets, change)
