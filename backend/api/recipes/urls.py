from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    FavoriteViewSet,
    RecipeViewSet,
    ShoppingCartViewSet,
    download_ingredients,
)

router = DefaultRouter()
router.register(r'', RecipeViewSet, basename='recipes')
router.register(r'(?P<id>\d+)', FavoriteViewSet, basename='favorite')
router.register(r'(?P<id>\d+)', ShoppingCartViewSet, basename='shopping')


urlpatterns = [
    path('download_shopping_cart/', download_ingredients),
    path('', include(router.urls)),
]
