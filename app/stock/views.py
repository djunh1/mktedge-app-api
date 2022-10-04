import datetime
import pytz

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from rest_framework import (
    viewsets,
    mixins,
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Stock
)
from stock import serializers

class StockViewSet(viewsets.ModelViewSet):
    """Manage the stock (runs) API

    Args:
        viewsets (_type_): _description_

    Returns:
        _type_: _description_
    """
    serializer_class = serializers.StockDetailSerializer
    queryset = Stock.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Stocks for authenticated user

        Returns:
            _type_: _description_
        """
        queryset = self.queryset
        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

    def get_serializer_class(self):
        """If using list endpoint, use the basic serializer.

        Returns:
            _type_: _description_
        """

        if self.action == 'list':
            return serializers.StockSerializer #return reference to class, not an instantiated object , IE no ()
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new Stock run object.
        Determine if going to use in final project.

        Args:
            serializer (_type_): _description_
        """
        serializer.save(user=self.request.user)


