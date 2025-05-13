from django.contrib import admin
from recipes.models import Recipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)

    def favorites_count(self, obj):
        """Получение количества добавлений в избранное."""
        return obj.in_favorites.count()
