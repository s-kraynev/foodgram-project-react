from django.urls import include, path

from .ingredients.urls import urlpatterns as ingredients_patterns
from .recipes.urls import urlpatterns as recipes_patterns
from .tags.urls import urlpatterns as tags_patterns
from .users.urls import urlpatterns as users_patterns

urlpatterns = [
    path('', include(ingredients_patterns)),
    path('', include(tags_patterns)),
    path('recipes/', include(recipes_patterns)),
    path('users/', include(users_patterns)),
    path('auth/', include('djoser.urls.authtoken')),
]
