from djoser.views import UserViewSet

from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (
    download_ingredients,
    FavoriteViewSet,
    TagsViewSet,
    RecipeViewSet,
    IngredientViewSet,
    SubscriptionsViewSet,
    SubscribeViewSet,
    ShoppingCartViewSet,
)

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagsViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes/(?P<id>\d+)', FavoriteViewSet, basename='favorite')
router.register(
    r'recipes/(?P<id>\d+)', ShoppingCartViewSet, basename='shopping'
)
router.register(
    r'users/subscriptions', SubscriptionsViewSet, basename='subscriptions'
),
router.register(
    r'users/(?P<id>[^/.]+)', SubscribeViewSet, basename='subscribe'
)

user_patterns = [
    path('', UserViewSet.as_view({'get': 'list'}), name='list_users'),
    path('', UserViewSet.as_view({'post': 'create'}), name='create_user'),
    path('me/', UserViewSet.as_view({'get': 'me'}), name='me'),
    path(
        'set_password/',
        UserViewSet.as_view({'post': 'set_password'}),
        name='set_password',
    ),
    re_path(
        '(?P<id>[^/.]+)/$',
        UserViewSet.as_view({'get': 'retrieve'}),
        name='get_user',
    ),
]

urlpatterns = [
    path('recipes/download_shopping_cart/', download_ingredients),
    path('', include(router.urls)),
    path('users/', include(user_patterns)),
    path('auth/', include('djoser.urls.authtoken')),
]
