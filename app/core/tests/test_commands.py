'''
Test Django management commands

DJacobson 8/26/2022
'''

from dataclasses import dataclass
from unittest.mock import patch
from io import StringIO
import pytz

from decimal import Decimal
import datetime

from pandas.testing import assert_frame_equal
from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase
from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import Stock

from app.settings import STATIC_ROOT


@patch("core.management.commands.wait_for_db.Command.check")
class WaitForDbCommandTests(SimpleTestCase):

    def test_wait_for_db_ready(self, patched_check):
        patched_check.return_value = True
        call_command('wait_for_db')
        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]
        call_command('wait_for_db')
        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])


def create_stock(**params):
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpassword123',
        )
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


class PopulateDbOnStartupTests(TestCase):

    def call_command(self, *args, **options):
        out = StringIO()
        call_command(
            'populate_stock_run_data_in_db'
        )
        return out.getvalue()

    def test_functions_do_not_get_called(self):
        """Methods will not run if there are stock objects in the DB
        """
        create_stock()
        #out = self.call_command()
        # self.assertEqual(out, "")


