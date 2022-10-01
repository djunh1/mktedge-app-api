from rest_framework import serializers

from core.models import Stock


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'ticker', 'start_date', 'end_date', 'sector', 'num_bases', 'length_run', 'pct_gain']
        read_only_fields = ['id']
