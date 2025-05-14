from django.urls import path

from api.views import RecipeViewSet

app_name = 'recipes'

urlpatterns = [
    path('<str:short_link>/',
         RecipeViewSet.as_view({'get': 'short_link_redirect'}),
         name='short-link-redirect'),
]
