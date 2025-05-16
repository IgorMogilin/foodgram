from django.contrib import admin

from recipes.models import Recipe, IngredientInRecipe


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    inlines = [IngredientInRecipeInline]

    def favorites_count(self, obj):
        """Получение количества добавлений в избранное."""
        return obj.in_favorites.count()
