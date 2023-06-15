from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


# TODO: think about custom pagination
class CustomPagination(LimitOffsetPagination):
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'response': data
        })