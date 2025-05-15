import django_filters
from django_filters import rest_framework as filters
from rest_framework import filters as drf_filters

from recipes.models import Recipe
from tags.models import Tag


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов с возможностью фильтрации по:
    - Нахождению в списке покупок
    - Нахождению в избранном
    - Тегам (множественный выбор)
    - Автору
    """

    is_in_shopping_cart = django_filters.CharFilter(
        method="filter_is_in_shopping_cart"
    )
    is_favorited = django_filters.CharFilter(method="filter_is_favorited")
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ("tags", "author", "is_in_shopping_cart", "is_favorited")

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрует рецепты по наличию в списке покупок пользователя.
        Возвращает только рецепты в списке покупок, если value=True.
        """

        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(
                in_carts__user=user
            )
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрует рецепты по наличию в избранном у пользователя.
        Возвращает только избранные рецепты, если value=True.
        """

        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(
                in_favorites__user=user
            )
        return queryset


class IngredientSearchFilter(drf_filters.SearchFilter):
    """Фильтр для поиска ингредиентов по названию.
    Поддерживает поиск по частичному совпадению без учета регистра.
    """

    search_param = 'name'
