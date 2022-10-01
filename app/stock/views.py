from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Stock
from stock import serializers

class StockViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.StockSerializer
    queryset = Stock.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Stocks for authenticated user

        Returns:
            _type_: _description_
        """
        return self.queryset.filter(user=self.request.user).order_by('-id')

