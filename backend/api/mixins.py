from rest_framework import status
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet


class ListViewSet(GenericViewSet, ListModelMixin):
    pass


class ListRetrieveViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin):
    pass


class DenyPutViewSet(ModelViewSet):
    def update(self, request, *args, **kwargs):
        partial = kwargs.get('partial', False)
        if not partial:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)
