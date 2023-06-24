from django.urls import include, path

from .common.urls import urlpatterns as common_patterns

urlpatterns = [
    path('', include(common_patterns)),
]
