from rest_framework import serializers, fields

from core.models import Stock


class StockSerializer(serializers.ModelSerializer):
    """Serializer for a stock

    Args:
        serializers (_type_): _description_
    """
    start_date = fields.DateField(input_formats=['%Y-%m-%d'])
    end_date = fields.DateField(input_formats=['%Y-%m-%d'])

    class Meta:
        model = Stock
        fields = [
            'id', 'ticker', 'start_date', 'end_date', 'sector', 'num_bases', 'length_run', 'pct_gain'
        ]
        read_only_fields = ['id']

class StockDetailSerializer(StockSerializer):
    """Serializer for stock run detail view

    Args:
        StockSerializer (_type_): _description_
    """
    class Meta(StockSerializer.Meta):
        fields = StockSerializer.Meta.fields + ['stock_run_notes']

    def create(self, validated_data):
        """Create a stock."""
        stock = Stock.objects.create(**validated_data)
        return stock

    def update(self, instance, validated_data):
        """Update stock."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
