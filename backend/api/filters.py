from django_filters import rest_framework as filters
from recipes.models import Recipe
from tags.models import Tag


class RecipeFilter(filters.FilterSet):
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart"
    )
    is_favorited = filters.BooleanFilter(method="filter_is_favorited")
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
        conjoined=False,
    )

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "author",
            "is_in_shopping_cart",
            "is_favorited",
        )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(recipes_in_shopping_cart__user=user)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorited_by_users__user=user)
        return queryset