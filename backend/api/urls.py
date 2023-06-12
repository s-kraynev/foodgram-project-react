from djoser.views import UserViewSet

from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api.views import (
    TagsViewSet,
    RecipeViewSet,
)

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagsViewSet, basename='tags')
#router.register(
#    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
#)
#router.register(
#    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
#    CommentViewSet,
#    basename='comments',
#)

user_patterns = [
    path('', UserViewSet.as_view({'post': 'create'}), name='create_user'),
    path('', UserViewSet.as_view({'get': 'list'}), name='list_users'),
    path('me/', UserViewSet.as_view({'get': 'me'}), name='me'),
    path('set_password/', UserViewSet.as_view({'post': 'set_password'}),
         name='set_password'),
    re_path('(?P<id>[^/.]+)/$', UserViewSet.as_view({'get': 'retrieve'}),
            name='get_user'),
]


urlpatterns = [
    path('', include(router.urls)),
    path('users/', include(user_patterns)),
    path('auth/', include('djoser.urls.authtoken')),
]