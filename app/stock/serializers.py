from importlib.metadata import requires
from rest_framework import serializers, fields

from core.models import(Stock, StockBase)

class StockBaseSerializer(serializers.ModelSerializer):
    """Serializer for a stock base object.

    Args:
        serializers (_type_): _description_
    """

    class Meta:
        model = StockBase
        fields = [
            'id', 'ticker', 'base_count', 'base_failure', 'bo_date',
            'vol_bo', 'vol_20', 'bo_vol_ratio', 'price_percent_range',
            'base_length',
            'sales_0qtr'
        ]
        read_only_fields = ['id']

class StockSerializer(serializers.ModelSerializer):
    """Serializer for a stock

    Args:
        serializers (_type_): _description_
    """
    start_date = fields.DateField(input_formats=['%Y-%m-%d'])
    end_date = fields.DateField(input_formats=['%Y-%m-%d'])

    bases = StockBaseSerializer(many=True, required=False)

    class Meta:
        model = Stock
        fields = [
            'id', 'ticker', 'start_date', 'end_date', 'sector',
            'num_bases', 'length_run', 'pct_gain', 'bases'
        ]
        read_only_fields = ['id']

class StockDetailSerializer(StockSerializer):
    """Serializer for stock run detail view

    Args:
        StockSerializer (_type_): _description_
    """
    class Meta(StockSerializer.Meta):
        fields = StockSerializer.Meta.fields + ['stock_run_notes']

    def _get_or_create_stock_bases(self, bases, stock):
        """Fetch or create stock bases

        Args:
            bases (_type_): _description_
            stock (_type_): _description_
        """
        auth_user = self.context['request'].user
        for base in bases:
            base_obj, created = StockBase.objects.get_or_create(
                user=auth_user,
                **base,
            )
            stock.bases.add(base_obj)

    def create(self, validated_data):
        """Create a stock."""
        bases = validated_data.pop('bases', [])
        stock = Stock.objects.create(**validated_data)
        self._get_or_create_stock_bases(bases, stock)
        return stock

    def update(self, instance, validated_data):
        """Update stock."""
        bases = validated_data.pop('bases', None)
        if bases is not None:
            instance.bases.clear()
            self._get_or_create_stock_bases(bases, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
