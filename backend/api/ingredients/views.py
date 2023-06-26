from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions

from api.common.filters import IngredientFilter
from api.common.mixins import ListRetrieveViewSet
from ingredients.models import Ingredient
from .serializers import IngredientSerializer


class IngredientViewSet(ListRetrieveViewSet):
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Ingredient.objects.all()
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
