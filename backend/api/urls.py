from djoser.views import UserViewSet

from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (
    FavoriteViewSet,
    TagsViewSet,
    RecipeViewSet,
    IngredientViewSet,
    SubscriptionViewSet,
)

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagsViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes/(?P<id>\d+)', FavoriteViewSet, basename='favorite')

user_patterns = [
    path('subscriptions/', SubscriptionViewSet.as_view({'get': 'list'}),
         name='get_subscriptions'),
    path('', UserViewSet.as_view({'post': 'create'}), name='create_user'),
    path('', UserViewSet.as_view({'get': 'list'}), name='list_users'),
    path('me/', UserViewSet.as_view({'get': 'me'}), name='me'),
    path('set_password/', UserViewSet.as_view({'post': 'set_password'}),
         name='set_password'),
    re_path('(?P<id>[^/.]+)/subscribe/$',
            SubscriptionViewSet.as_view({'post': 'subscribe'}),
            name='subscribe'),
    re_path('(?P<id>[^/.]+)/subscribe/$',
            SubscriptionViewSet.as_view({'delete': 'subscribe'}),
            name='unsubscribe'),
    re_path('(?P<id>[^/.]+)/$', UserViewSet.as_view({'get': 'retrieve'}),
            name='get_user'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('users/', include(user_patterns)),
    path('auth/', include('djoser.urls.authtoken')),
]
