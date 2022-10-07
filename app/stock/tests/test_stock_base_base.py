import datetime
from decimal import Decimal
import pytz

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Stock
from core.models import StockBase
from core import models

from stock.serializers import StockBaseSerializer

STOCK_BASE_URL = reverse('stock:stockbase-list')


def create_user(email='gengis_car@example.com', password='testp@ssw0rds'):
    """Create and return user."""
    return get_user_model().objects.create_user(email=email, password=password)

def create_stock():
    # TODO: convert this from datetime to date.  DB only takes a date anyway but this works for now
    stock = models.Stock.objects.create(
            user=create_user(),
            ticker='NVDA-1',
            start_date=datetime.datetime(2015, 9, 28, 0, 0, 0, 0, pytz.UTC),
            end_date=datetime.datetime(2018, 10, 8, 0, 0, 0, 0, pytz.UTC),
            num_bases=9,
            sector='Electronic Technology',
            length_run=157,
            pct_gain=Decimal('1109.0'),
        )
    return stock

class PublicStockBaseApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_authorization_required(self):
        res = self.client.get(STOCK_BASE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateStockBaseApiTests(TestCase):

    def setUp(self):
        self.user = create_user(email="johnTheCar@example.com")
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_fetch_stock_bases(self):
        stock = create_stock()
        StockBase.objects.create(user=self.user,
                                 stock_reference=stock,
                                 ticker='AMD-1',
                                 base_count=4,
                                 base_failure='n',
                                 base_length=4,
                                 price_percent_range=Decimal('24.3'),
                                 bo_date=datetime.datetime(2015, 7, 28, 0, 0, 0, 0, pytz.UTC))

        stock_base = StockBase.objects.create(user=self.user,
                                 stock_reference=stock,
                                 ticker='AMD-1',
                                 base_count=5,
                                 base_failure='y',
                                 base_length=4,
                                 price_percent_range=Decimal('24.3'),
                                 bo_date=datetime.datetime(2015, 9, 28, 0, 0, 0, 0, pytz.UTC))

        res = self.client.get(STOCK_BASE_URL)

        stock_bases = StockBase.objects.all().order_by('-ticker')
        serializer = StockBaseSerializer(stock_bases, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_stock_base_limited_to_user(self):
        """Test list of stock base data is limited to authenticated user.
           Eventually will not be the case
        """
        user2 = create_user(email='toyboata@example.com')
        stock = create_stock()
        other_stock = models.Stock.objects.create(
                                user=user2,
                                ticker='NVDA-1',
                                start_date=datetime.datetime(2015, 9, 28, 0, 0, 0, 0, pytz.UTC),
                                end_date=datetime.datetime(2018, 10, 8, 0, 0, 0, 0, pytz.UTC),
                                num_bases=9,
                                sector='Electronic Technology',
                                length_run=157,
                                pct_gain=Decimal('1109.0'),
                            )

        StockBase.objects.create(user=user2,
                                 stock_reference=other_stock,
                                 ticker='AMD-1',
                                 base_count=4,
                                 base_failure='n',
                                 base_length=4,
                                 price_percent_range=Decimal('24.3'),
                                 bo_date=datetime.datetime(2015, 7, 28, 0, 0, 0, 0, pytz.UTC))


        stock_base = StockBase.objects.create(user=self.user,
                                 stock_reference=stock,
                                 ticker="AMD-2",
                                 base_count=5,
                                 base_failure='y',
                                 base_length=4,
                                 price_percent_range=Decimal('24.3'),
                                 bo_date=datetime.datetime(2015, 9, 28, 0, 0, 0, 0, pytz.UTC))

        res = self.client.get(STOCK_BASE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        print(res.data[0])
        self.assertEqual(res.data[0]['ticker'], stock_base.ticker)
        self.assertEqual(res.data[0]['id'], stock_base.id)
