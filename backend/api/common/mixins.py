from django.db.models import prefetch_related_objects
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class ListViewSet(GenericViewSet, ListModelMixin):
    pass


class ListRetrieveViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin):
    pass


class PatchModelMixin:
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        queryset = self.filter_queryset(self.get_queryset())
        if queryset._prefetch_related_lookups:
            instance._prefetched_objects_cache = {}
            prefetch_related_objects([
                instance], *queryset._prefetch_related_lookups
            )
        return Response(serializer.data)

    def perform_update(self, serializer):
         serializer.save()


class DenyPutViewSet(CreateModelMixin,
                     ListModelMixin,
                     RetrieveModelMixin,
                     DestroyModelMixin,
                     PatchModelMixin,
                     GenericViewSet
):
    pass

