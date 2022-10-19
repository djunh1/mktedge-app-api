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
    Stock,
    StockBase
)
from stock import serializers


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'bases',
                OpenApiTypes.STR,
                description='Comma separated list of stock base IDs to filter',
            ),
        ]
    )
)
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

    def _params_to_int(self, qs):
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Stocks for authenticated user

        Returns:
            _type_: _description_
        """
        stock_bases = self.request.query_params.get('bases')
        queryset = self.queryset
        if stock_bases:
            base_ids = self._params_to_int(stock_bases)
            queryset = queryset.filter(bases__id__in=base_ids)

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

class StockBaseViewSet(mixins.DestroyModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """Manage stock bases

    Args:
        mixins (_type_): _description_
        viewsets (_type_): _description_
    """
    serializer_class = serializers.StockBaseSerializer
    queryset = StockBase.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('ticker') #might break since this is a fk

