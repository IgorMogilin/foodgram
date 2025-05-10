from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import (Ingredient, IngredientInRecipe, Recipe, Tag,
                            UserRecipeRelation)
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Subscriptions, User

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import PageLimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (AvatarSerializer, IngredientSerializer,
                          RecipeCreateUpdateSerializer, RecipeSerializer,
                          SubscriptionCreateSerializer, SubscriptionDeleteValidator,
                          SubscriptionSerializer, TagSerializer,
                          UserRecipeRelationSerializer, UserSerializer)


class UserViewSet(DjoserUserViewSet):
    """ViewSet для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageLimitPagination

    def get_permissions(self):
        """Определяет права доступа в зависимости от действия.

        Особые условия:
        - Для эндпоинта 'me' требуется аутентификация
        - Для остальных действий применяются стандартные правила Djoser

        Returns:
            list: Список классов разрешений для текущего действия
        """

        if self.action == "me":
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(
        detail=False,
        methods=['put'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Обновляет аватар текущего пользователя."""

        user = request.user
        serializer = AvatarSerializer(
            user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удаляет аватар текущего пользователя."""

        user = request.user
        if user.avatar:
            user.avatar.delete()
            user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='subscribe'
    )
    def subscribe(self, request, id=None):
        """Добавляет подписку на пользователя."""

        author = get_object_or_404(User, id=id)
        serializer = SubscriptionCreateSerializer(
            data=request.data,
            context={'request': request, 'author': author}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = SubscriptionSerializer(
            author, context={'request': request}
        )
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        """Удаляет подписку на пользователя."""

        author = get_object_or_404(User, id=id)
        serializer = SubscriptionDeleteValidator(
            data={}, context={'request': request, 'author': author}
        )
        serializer.is_valid(raise_exception=True)
        Subscriptions.objects.filter(user=request.user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        pagination_class=PageLimitPagination
    )
    def subscriptions(self, request):
        """Возвращает список подписок текущего пользователя."""

        user = request.user
        queryset = User.objects.filter(subscribers__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с тегами (только чтение)."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с ингридиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filterset_class = IngredientSearchFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['^name']


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с рецептами."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    ]
    pagination_class = PageLimitPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Определяет сериализатор в зависимости от действия."""

        if self.action in ("create", "update", "partial_update"):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='(?P<type>favorite|shopping_cart)'
    )
    def add_to_list(self, request, pk=None, type=None):
        """Добавляет рецепт в избранное или в корзину."""

        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        if type == 'shopping_cart':
            relation_type = UserRecipeRelation.CART
        elif type == 'favorite':
            relation_type = UserRecipeRelation.FAVORITE
        else:
            return Response(
                {'errors': 'Неверный тип действия'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserRecipeRelationSerializer(
            data={
                'user': user.id,
                'recipe': recipe.id,
                'relation_type': relation_type
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @add_to_list.mapping.delete
    def remove_from_list(self, request, pk=None, type=None):
        """Удаляет рецепт из избранного или из корзины."""

        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        if type == 'shopping_cart':
            relation_type = UserRecipeRelation.CART
        elif type == 'favorite':
            relation_type = UserRecipeRelation.FAVORITE
        else:
            return Response(
                {'errors': 'Неверный тип действия'},
                status=status.HTTP_400_BAD_REQUEST
            )

        deleted_count, _ = UserRecipeRelation.objects.filter(
            user=user, recipe=recipe, relation_type=relation_type
        ).delete()

        if not deleted_count:
            return Response(
                {'errors': 'Рецепт не найден в списке'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        """Генерирует текстовый файл со списком покупок."""

        ingredients = IngredientInRecipe.objects.filter(
            recipe__user_relations__relation_type=UserRecipeRelation.CART
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total=Sum('amount'))

        text = 'Список покупок:\n\n'
        for ing in ingredients:
            text += (
                f"{ing['ingredient__name']} "
                f"({ing['ingredient__measurement_unit']}) - "
                f"{ing['total']}\n"
            )

        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[AllowAny],
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        """Возвращает абсолютную ссылку на рецепт."""

        recipe = get_object_or_404(Recipe, id=pk)
        short_link = f'{request.get_host()}/{recipe.short_link}/'
        return Response({
            'short-link': short_link
        })

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[AllowAny],
        url_path='short-link-redirect'
    )
    def get_short_link(self, request, short_link):
        """Возвращает короткую ссылку для рецепта."""
        recipe = get_object_or_404(Recipe, short_link=short_link)
        return Response({"short_link": recipe.short_link})
