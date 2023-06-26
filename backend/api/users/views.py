from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from api.common.mixins import ListViewSet
from users.models import Follow
from .serializers import SubscribeSerializer

User = get_user_model()


class SubscribeViewSet(ViewSet):
    queryset = Follow.objects.all()

    def get_author(self):
        return get_object_or_404(User, id=self.kwargs.get('id'))

    @action(
        methods=['POST'],
        detail=False,
        url_path='subscribe',
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author = self.get_author()
        # pass context for correct work is_subscribed in User serializator
        serializer = SubscribeSerializer(
            author, data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        Follow.objects.create(user=user, author=author)
        # sorting number of recipes
        recipes_limit = request.query_params.get('recipes_limit')
        display_data = []
        iteration_data = serializer.data
        if isinstance(iteration_data, dict):
            iteration_data = [iteration_data]

        for author in iteration_data:
            display_data.append(author.copy())
            if recipes_limit is not None:
                display_data[-1]['recipes'] = display_data[-1]['recipes'][
                    : int(recipes_limit)
                ]
        return Response(display_data, status=status.HTTP_200_OK)

    @subscribe.mapping.delete
    def unsubscribe(self, request, **kwargs):
        user = request.user
        author = self.get_author()
        # pass context for correct work is_subscribed in User serializator
        serializer = SubscribeSerializer(
            author, data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        Follow.objects.get(user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# NOTE: ViewSet does not have paginate_queryset and I got error:
# 'SubscriptionsViewSet' object has no attribute 'paginate_queryset'
# It happens because:
# - ViewSet has not method 'paginate_queryset'
# - ListViewSet is inherited from GenericViewSet
# - GenericViewSet extends simple ViewSet and adds paginate_queryset method
class SubscriptionsViewSet(ListViewSet):
    queryset = Follow.objects.all()

    def list(self, request, *args, **kwargs):
        authors = Follow.objects.filter(user=request.user).values_list(
            'author', flat=True
        )
        queryset = User.objects.filter(id__in=authors).all()
        page = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            page, many=True, context={'request': request}
        )
        # sorting number of recipes
        recipes_limit = request.query_params.get('recipes_limit')
        display_data = []
        for author in serializer.data:
            display_data.append(author.copy())
            if recipes_limit is not None:
                display_data[-1]['recipes'] = display_data[-1]['recipes'][
                    : int(recipes_limit)
                ]
        return self.get_paginated_response(display_data)
