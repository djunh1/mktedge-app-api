import csv
import os
from datetime import datetime
from core.models import Stock

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

import pandas as pd

from app.settings import STATIC_ROOT

class Command(BaseCommand):
    """Populates the database with the CSV file upon startup.

    Args:
        BaseCommand (Command): Inherit from BaseCommand object
    """

    def handle(self, *args, **options):
        file_path = STATIC_ROOT + "/data/"
        file_name = "stock_summary.csv"

        # Uncomment to generate test data
        # df = self.import_and_filter_csv(file_path, file_name)

        if not Stock.objects.exists():
            self.stdout.write("No stock objects exist in the DB, importing them...")
            df = self.import_and_filter_csv(file_path, file_name)
            user = self.create_or_return_first_user()
            self.add_stocks_to_db(df, user)
        else:
            self.stdout.write("Stock DB is populated, no further action performed...\n")

    def import_and_filter_csv(self, file_path, file_name):
        df = pd.read_csv(os.path.join(file_path, file_name))
        symbols_to_drop = ['tbd', 'Tbd']
        date_columns = ['start_date', 'end_date']
        for symbol in symbols_to_drop:
            df.drop(df.index[df['end_date'] == symbol], inplace = True)
        df = df.dropna(subset=['end_date'])
        for col in date_columns:
            df[col] =  pd.to_datetime(df[col])
        self.generate_test_data(df,"import_filter_test.csv", False)
        return df

    def add_stocks_to_db(self, df, user):
        for idx, row in df.iterrows():
            if idx==1:
                pass
            else:
                print('Adding stock data for {} into DB '.format(row['ticker']))
                Stock.objects.get_or_create(ticker=row['ticker'],
                                     start_date=row['start_date'],
                                     end_date=row['end_date'],
                                     sector=row['sector'],
                                     num_bases=row['num_bases'],
                                     length_run=row['length_run'],
                                     pct_gain=row['pct_gain'],
                                     user_id=user.id,
                                     stock_run_notes='Initial stock base information creation.')

    def create_or_return_first_user(self):
        if get_user_model().objects.get(pk=1):
            user = get_user_model().objects.get(pk=1) #TODO: going to need a way to get specific user..
        else:
            user = get_user_model().objects.create_user(os.environ.get('USER_EMAIL'), os.environ.get('USER_PASS'))
        return user

    @staticmethod
    def generate_test_data(df, file_name, run_test_data_generator):
        file_path = STATIC_ROOT + "/data/test/"
        if run_test_data_generator:
            csv_dir = file_path
            df.to_csv(csv_dir + file_name, encoding='utf-8', float_format='%.2f')



