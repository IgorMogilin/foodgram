from django.urls import include, path
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from api.views import (
    UserViewSet, TagViewSet,
    IngredientViewSet, RecipeViewSet,
    CustomAuthToken, APILogoutView,
    get_short_link, redirect_short_link  # Добавьте новые импорты
)
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('api/auth/', include('djoser.urls')),
    path('api/auth/token/login/', CustomAuthToken.as_view(), name='token_login'),
    path('api/auth/token/logout/', APILogoutView.as_view(), name='token_logout'),
    path('api/', include(router.urls)),
    path('api/recipes/<int:recipe_id>/get-link/', get_short_link, name='get-short-link'),  # Новый путь
    path('s/<str:code>/', redirect_short_link, name='redirect-short-link'),  # Редирект
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)