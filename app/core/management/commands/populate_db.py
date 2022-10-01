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
        self.stdout.write("Populating database with CSV data...")
        file_path = STATIC_ROOT + "/data/"

        df = pd.read_csv(os.path.join(file_path, "stock_summary.csv"))

        symbols_to_drop = ['tbd', 'Tbd']
        date_columns = ['start_date', 'end_date']

        for symbol in symbols_to_drop:
            df.drop(df.index[df['end_date'] == symbol], inplace = True)
        df = df.dropna(subset=['end_date'])
        for col in date_columns:
            df[col] =  pd.to_datetime(df[col])

        user = self.create_or_return_first_user()

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
                                     user_id=user.id)

    def create_or_return_first_user(self):
        if get_user_model().objects.get(pk=1):
            user = get_user_model().objects.get(pk=1)
        else:
            user = get_user_model().objects.create_user(os.environ.get('USER_EMAIL'), os.environ.get('USER_PASS'))
        return user



