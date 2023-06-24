from rest_framework import permissions

from api.common.mixins import ListRetrieveViewSet
from tags.models import Tag

from .serializers import TagSerializer


class TagsViewSet(ListRetrieveViewSet):
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Tag.objects.all()
    pagination_class = None
