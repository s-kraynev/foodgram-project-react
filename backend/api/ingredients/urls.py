from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet

router = DefaultRouter()
router.register('', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
]
