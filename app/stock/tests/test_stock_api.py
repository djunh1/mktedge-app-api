from decimal import Decimal
import datetime
import pytz

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Stock

from stock.serializers import StockSerializer

STOCKS_URL = reverse('stock:stock-list')

def create_stock(user, **params):
    defaults = {
        'ticker':'amd-1',
        'start_date' : datetime.datetime(2020, 4, 27, 0, 0, 0, 0, pytz.UTC),
        'end_date' : datetime.datetime(2022, 4, 27, 0, 0, 0, 0, pytz.UTC) ,
        'num_bases' : 4,
        'sector': 'Electronic Technology',
        'length_run': 90,
        'pct_gain': Decimal(123.4),
    }

    defaults.update(params)

    stock = Stock.objects.create(user=user, **defaults)
    return stock

class PublicStockAPITests(TestCase):
    """unauthenticated API requests

    Args:
        TestCase (_type_): _description_
    """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(STOCKS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateStockAPITests(TestCase):
    """Authenticated requests

    Args:
        TestCase (_type_): _description_
    """
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_fetch_stocks(self):
        """Fetch list of stocks
        """

        create_stock(user=self.user)
        create_stock(user=self.user)

        res = self.client.get(STOCKS_URL)

        stocks = Stock.objects.all().order_by('-id')
        serializer = StockSerializer(stocks, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_stock_list_only_for_user(self):
        someone_else = get_user_model().objects.create_user(
            'other@example.com',
            'password123',
        )

        create_stock(user=someone_else)
        create_stock(user=self.user)

        res = self.client.get(STOCKS_URL)

        stocks = Stock.objects.filter(user=self.user)
        serializer = StockSerializer(stocks, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)






