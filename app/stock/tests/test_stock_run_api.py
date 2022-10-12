from decimal import Decimal
import datetime
import pytz

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (Stock, StockBase)


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

def create_user(**params):
    return get_user_model().objects.create_user(**params)

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
        self.user  = create_user(email='test@example.com', password='testP@ssw0rd24601')
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
        someone_else = create_user(email='otherUser@example.com', password='testP@ssw0rd24601')

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

        # TODO: do I need an ID to create these?
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

        self.assertEqual(stock.ticker, "amd-1")
        self.assertEqual(stock.start_date, datetime.date(2015, 10, 20))
        self.assertEqual(stock.end_date, datetime.date(2018, 9, 20))
        self.assertEqual(stock.sector, "Electronic Technology")
        self.assertEqual(stock.num_bases, 3)
        self.assertEqual(stock.length_run, 44)
        self.assertEqual(stock.pct_gain, round(Decimal(123.4),2))
        self.assertEqual(stock.stock_run_notes, "a note")
        self.assertEqual(stock.user, self.user)

    def test_partial_update(self):
        """Update part of stock run object
        """
        original_length_run = 25
        stock = create_stock(ticker='UCO-1', start_date=datetime.date(2015, 7, 20),  end_date=datetime.date(2017, 2, 20),
                             sector='Energy Minerals', num_bases=3, length_run=original_length_run, pct_gain=Decimal(54.7),  user=self.user,
                             stock_run_notes='Partial update test.')

        payload = {'ticker': 'UCO-2'}
        url = detail_url(stock.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        stock.refresh_from_db()
        self.assertEqual(stock.ticker, payload['ticker'])
        self.assertEqual(stock.length_run, original_length_run)
        self.assertEqual(stock.user, self.user)

    def test_full_update(self):
        """Test full update of stock run."""
        stock = create_stock(ticker='TSLA-1', start_date=datetime.date(2016, 7, 20),  end_date=datetime.date(2017, 2, 20),
                             sector='Energy Minerals', num_bases=3, length_run=56, pct_gain=Decimal(300.7),  user=self.user,
                             stock_run_notes='Tesla run #1')

        payload = {
            "ticker": "tsla-3",
            "start_date": "2015-7-20",
            "end_date": "2020-09-20",
            "sector": "Electronic Technology",
            "num_bases": 5,
            "length_run": 65,
            "pct_gain": "350.7",
            "stock_run_notes": "Tesla run number #3 corrected"
        }
        url = detail_url(stock.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        stock.refresh_from_db()

        self.assertEqual(stock.ticker, "tsla-3")
        self.assertEqual(stock.start_date, datetime.date(2015, 7, 20))
        self.assertEqual(stock.end_date, datetime.date(2020, 9, 20))
        self.assertEqual(stock.sector, "Electronic Technology")
        self.assertEqual(stock.num_bases, 5)
        self.assertEqual(stock.length_run, 65)
        self.assertEqual(stock.pct_gain, round(Decimal(350.7),2))
        self.assertEqual(stock.stock_run_notes, "Tesla run number #3 corrected")
        self.assertEqual(stock.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the stock run user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        stock = create_stock(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(stock.id)
        self.client.patch(url, payload)

        stock.refresh_from_db()
        self.assertEqual(stock.user, self.user)

    def test_delete_stock(self):
        """Test deleting a stock successful."""
        stock = create_stock(user=self.user)

        url = detail_url(stock.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Stock.objects.filter(id=stock.id).exists())

    def test_other_users_stock_error(self):
        """Test trying to delete another users stock gives error."""
        new_user = create_user(email='user2@example.com', password='test1234')
        stock = create_stock(user=new_user)

        url = detail_url(stock.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Stock.objects.filter(id=stock.id).exists())

    def test_create_stock_with_new_stock_bases(self):
        """Test creating a stock with multiple new stock bases."""
        payload = {
            "ticker": "SQ-1",
            "start_date": "2016-10-31",
            "end_date": "2018-10-8",
            "sector": "Technology Services",
            "num_bases": 6,
            "length_run": 101,
            "pct_gain": Decimal("738.5"),
            "stock_run_notes": "SQ stock run",
            "bases": [ {
                'ticker': 'SQ-1',
                'base_count': 0,
                'bo_date': '2016-10-31'
            },
            {
                'ticker': 'SQ-1',
                'base_count': 0,
                'bo_date': '2017-2-21',
                'base_failure': 'n',
                'vol_bo':78210911,
                'vol_20':24972449,
                'bo_vol_ratio': Decimal('3.13'),
                'price_percent_range': Decimal('10.3'),
                'base_length': Decimal('10')
            },
            ]
        }
        res = self.client.post(STOCKS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        stocks = Stock.objects.filter(user=self.user)
        self.assertEqual(stocks.count(), 1)
        stock = stocks[0]
        self.assertEqual(stock.bases.count(), 2)
        for stockbase in payload['bases']:
            exists = stock.bases.filter(
                ticker=stockbase['ticker'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredient(self):
        """Test creating a new recipe with existing stock base."""
        stock_base = StockBase.objects.create(user=self.user, ticker='SQ-1', base_count=0,
                    bo_date=datetime.date(2016, 10, 31))
        payload = {
            "ticker": "SQ-1",
            "start_date": "2016-10-31",
            "end_date": "2018-10-8",
            "sector": "Technology Services",
            "num_bases": 6,
            "length_run": 101,
            "pct_gain": Decimal("738.5"),
            "stock_run_notes": "SQ stock run",
            "bases": [ {
                'ticker': 'SQ-1',
                'base_count': 0,
                'bo_date': '2016-10-31'
            },
            {
                'ticker': 'SQ-1',
                'base_count': 0,
                'bo_date': '2017-2-21',
                'base_failure': 'n',
                'vol_bo':78210911,
                'vol_20':24972449,
                'bo_vol_ratio': Decimal('3.13'),
                'price_percent_range': Decimal('10.3'),
                'base_length': Decimal('10')
            },
            ]
        }
        res = self.client.post(STOCKS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        stocks = Stock.objects.filter(user=self.user)
        self.assertEqual(stocks.count(), 1)
        stock = stocks[0]
        self.assertEqual(stock.bases.count(), 2) #only two stock bases since we need 1 associated with a stock run only
        self.assertIn(stock_base, stock.bases.all())
        for stockbase in payload['bases']:
            exists = stock.bases.filter(
                ticker=stockbase['ticker'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)








