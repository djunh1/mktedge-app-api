from decimal import Decimal
import datetime
import pytz

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Stock


from stock.serializers import (
    StockSerializer,
    StockDetailSerializer,
)

STOCKS_URL = reverse('stock:stock-list')

def detail_url(stock_id):
    """Stock detail url

    Args:
        stock_id (_type_): _description_
    """
    return reverse('stock:stock-detail', args=[stock_id])

def create_stock(user, **params):
    defaults = {
        'ticker':'amd-1',
        'start_date' : datetime.date(2015, 10, 20),
        'end_date' : datetime.date(2017, 10, 20) ,
        'num_bases' : 4,
        'sector': 'Electronic Technology',
        'length_run': 90,
        'pct_gain': Decimal(123.4),
        'stock_run_notes': '',
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
            'testP@ssw0rd24601',
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

    def test_get_stock_detail(self):
        stock = create_stock(user=self.user)
        url = detail_url(stock.id)
        res = self.client.get(url)

        serializer = StockDetailSerializer(stock)
        self.assertEqual(res.data, serializer.data)

    def test_create_stock_run(self):
        """Creating stock run object
        """
        payload = {
            "id": 1,
            "ticker": "amd-1",
            "start_date": "2015-10-20",
            "end_date": "2018-09-20",
            "sector": "Electronic Technology",
            "num_bases": 3,
            "length_run": 44,
            "pct_gain": "123.4",
            "stock_run_notes": "a note"
        }


        res = self.client.post(STOCKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        stock = Stock.objects.get(id=res.data['id'])

        # for k, v in payload.items():
        #     self.assertEqual(getattr(stock, k), v)
        self.assertEqual(stock.ticker, "amd-1")
        self.assertEqual(stock.start_date, datetime.date(2015, 10, 20))
        self.assertEqual(stock.end_date, datetime.date(2018, 9, 20))
        self.assertEqual(stock.sector, "Electronic Technology")
        self.assertEqual(stock.num_bases, 3)
        self.assertEqual(stock.length_run, 44)
        self.assertEqual(stock.pct_gain, round(Decimal(123.4),2))
        self.assertEqual(stock.stock_run_notes, "a note")
        self.assertEqual(stock.user, self.user)






