import csv
import os

import numpy as np
from datetime import datetime
from core.models import (StockBase, Stock)

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

import pandas as pd

from app.settings import STATIC_ROOT

class Command(BaseCommand):
    """Populates the database with stock run CSV data.

    Args:
        BaseCommand (Command): Inherit from BaseCommand object
    """

    def handle(self, *args, **options):
        file_path = STATIC_ROOT + "/data/"
        file_name = "stock_base_data.csv"

        user = get_user_model().objects.get(email=os.environ.get('USER_EMAIL'))

        # Uncomment to generate test data
        # df = self.import_and_filter_csv(file_path, file_name)

        if not StockBase.objects.exists():
            self.stdout.write("No stock base data exists in the DB.  Importing data.\n")
            df = self.import_and_filter_csv(file_path, file_name)
            self.add_stocks_to_db(df, user)
        else:
            self.stdout.write("Stock base data exists in DB, no further action performed.\n")

    def import_and_filter_csv(self, file_path, file_name):
        df = pd.read_csv(os.path.join(file_path, file_name))

        # maybe don't need
        # columns_with_nan = ['base_length']
        # for col in columns_with_nan:
        #     df[col] = df[col].replace(np.nan, 0)
        # df['base_failure'] = df['base_failure'].fillna("n")


        date_columns = ['bo_date']
        for col in date_columns:
            df[col] =  pd.to_datetime(df[col])
        # self.generate_test_data(df,"import_filter_test.csv", False)

        return df

    def add_stocks_to_db(self, df, user):
        for idx, row in df.iterrows():
            if idx==8000:
                break
            else:
                print('Adding stock base data for ticker : {} base[{}] into DB '.format(row['ticker'], row['base_count']))
                try:
                   stock = Stock.objects.get(ticker__iexact=row['ticker'])
                   StockBase.objects.get_or_create(ticker=row['ticker'],
                                                    base_count=row['base_count'],
                                                    base_failure='n' if pd.isnull(row['base_failure']) else row['base_failure'],
                                                    bo_date=row['bo_date'],
                                                    vol_bo=row['vol_bo'],
                                                    vol_20=row['vol_20'],
                                                    bo_vol_ratio=row['bo_vol_ratio'],
                                                    price_percent_range=None if pd.isnull(row['price_percent_range']) else row['price_percent_range'],
                                                    base_length=None if pd.isnull(row['base_length']) else row['base_length'],
                                                    user_id=user.id,
                                                    stock_reference_id=stock.id,
                                                    sales_0qtr=None if pd.isnull(row['sales_0qtr']) else row['sales_0qtr'])
                except ObjectDoesNotExist:
                    print("{} does not exist".format(row['ticker']))





