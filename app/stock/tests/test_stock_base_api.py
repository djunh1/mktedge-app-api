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

def detail_url(stock_base_id):
    return reverse('stock:stockbase-detail', args=[stock_base_id])

def create_user(email='gengis_car@example.com', password='testp@ssw0rds'):
    """Create and return user."""
    return get_user_model().objects.create_user(email=email, password=password)

def create_stock(user):
    # TODO: convert this from datetime to date.  DB only takes a date anyway but this works for now
    stock = models.Stock.objects.create(
            user=user,
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
        stock = create_stock(self.user)
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
        stock = create_stock(self.user)
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
        self.assertEqual(res.data[0]['ticker'], stock_base.ticker)
        self.assertEqual(res.data[0]['id'], stock_base.id)

    def test_update_stock_base(self):
        stock = create_stock(self.user)
        stock_base = StockBase.objects.create(user=self.user,
                                 stock_reference=stock,
                                 ticker="FSLR-2",
                                 base_count=5,
                                 base_failure='y',
                                 base_length=4,
                                 price_percent_range=Decimal('24.3'),
                                 bo_date=datetime.datetime(2015, 9, 28, 0, 0, 0, 0, pytz.UTC))

        payload = {'ticker': 'FSLR-1'}
        url = detail_url(stock_base.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        stock_base.refresh_from_db()
        self.assertEqual(stock_base.ticker, payload['ticker'])

    def test_delete_stock_base(self):
        stock = create_stock(self.user)
        stock_base = StockBase.objects.create(user=self.user,
                                 stock_reference=stock,
                                 ticker="TSLA-1",
                                 base_count=3,
                                 base_failure='n',
                                 base_length=15,
                                 price_percent_range=Decimal('43.3'),
                                 bo_date=datetime.datetime(2020, 7, 28, 0, 0, 0, 0, pytz.UTC))

        url = detail_url(stock_base.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        stock_bases = StockBase.objects.filter(user=self.user)
        self.assertFalse(stock_bases.exists())

    def test_update_stock_base(self):
        stock = create_stock(self.user)
        stock_base = StockBase.objects.create(user=self.user,
                                 stock_reference=stock,
                                 ticker="NVDA-1",
                                 base_count=5,
                                 base_failure='y',
                                 base_length=4,
                                 price_percent_range=Decimal('24.3'),
                                 bo_date=datetime.datetime(2015, 9, 28, 0, 0, 0, 0, pytz.UTC))
        payload = {
                    'ticker': 'NVDA-1',
                    'base_count': 0,
                    'bo_date': '2017-2-21',
                    'base_failure': 'n',
                    'vol_bo':78210911,
                    'vol_20':24972449,
                    'bo_vol_ratio': Decimal('3.13'),
                    'price_percent_range': Decimal('10.3'),
                    'base_length': Decimal('10')
                  }

        url = detail_url(stock_base.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        stock_base.refresh_from_db()
        self.assertEqual(stock_base.ticker, payload['ticker'])


