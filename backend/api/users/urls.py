from django.urls import include, path, re_path
from djoser.views import UserViewSet
from rest_framework.routers import DefaultRouter

from .views import SubscribeViewSet, SubscriptionsViewSet

router = DefaultRouter()
router.register(
    r'subscriptions', SubscriptionsViewSet, basename='subscriptions'
),
router.register(r'(?P<id>[^/.]+)', SubscribeViewSet, basename='subscribe')

urlpatterns = [
    path(
        '',
        UserViewSet.as_view(
            {
                'get': 'list',
                'post': 'create',
            }
        ),
        name='create_list_users',
    ),
    path('', include(router.urls)),
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
