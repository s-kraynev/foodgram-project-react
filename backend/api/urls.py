from django.urls import include, path

from .common.urls import urlpatterns as common_patterns
from .ingredients.urls import urlpatterns as ingredients_patterns
from .tags.urls import urlpatterns as tags_patterns

urlpatterns = [
    path('', include(common_patterns)),
    path('', include(ingredients_patterns)),
    path('', include(tags_patterns)),
]
