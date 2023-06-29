from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    RecipeViewSet,
    download_ingredients,
)

router = DefaultRouter()
router.register(r'', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('download_shopping_cart/', download_ingredients),
    path('', include(router.urls)),
]
