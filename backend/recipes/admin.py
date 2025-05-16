from django.contrib import admin
from django.core.exceptions import ValidationError

from recipes.models import Recipe, IngredientInRecipe


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientInRecipeInline]
    list_display = ('name', 'author', 'favorites_count')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)

    def favorites_count(self, obj):
        return obj.in_favorites.count()

    def save_model(self, request, obj, form, change):
        if not obj.image:
            raise ValidationError("Нельзя сохранить рецепт без изображения.")
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if not form.instance.ingredients.exists():
            raise ValidationError("Нельзя сохранить рецепт без ингредиентов.")
