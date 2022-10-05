
"""
Tests for models.

DJacobson 8/27/2022
"""
import pytz

from decimal import Decimal
import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email='user@example.com', password='testpass123'):
    """Create a return a new user."""
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):

    def test_create_user_with_email_success(self):
        email = "unassisted@example.com"
        password = 'pastalavista'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_new_user_email_normalized(self):
        sample_emails = [
            ['bergeron@EXAMPLE.com', 'bergeron@example.com'],
            ['Pasternak@Example.com', 'Pasternak@example.com'],
            ['MARCHAND@EXAMPLE.COM', 'MARCHAND@example.com'],
            ['krecji@example.COM', 'krecji@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'hatTrick345')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_exception(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test234')

    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser(
            'ribbentrop@example.com',
            'test2345'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_stock(self):
        """Will not use, but create a stock object in DB
        """
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpassword123',
        )

        stock = models.Stock.objects.create(
            user=user,
            ticker='APG-1',
            start_date=datetime.datetime(2020, 4, 27, 0, 0, 0, 0, pytz.UTC),
            end_date=datetime.datetime(2022, 1, 18, 0, 0, 0, 0, pytz.UTC),
            num_bases=5,
            sector='Electronic Technology',
            length_run=90,
            pct_gain=Decimal('205.3'),
        )

        self.assertEqual(str(stock), stock.ticker)

    def test_create_stock_base(self):
        """Test stock base object creation is successful."""
        user = create_user()
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
        base = models.StockBase.objects.create(
            user=user,
            ticker=stock,
            base_count=5,
            base_failure='n',
            bo_date=datetime.datetime(2019, 5, 9, 0, 0, 0, 0, pytz.UTC),
            vol_bo=371198872,
            vol_20=175539248,
            bo_vol_ratio=Decimal('2.11'),
            price_percent_range=Decimal('11.3'),
            base_length=6,
            sales_0qtr = Decimal('1428.0'),
        )

        self.assertEqual(stock, base.ticker)
