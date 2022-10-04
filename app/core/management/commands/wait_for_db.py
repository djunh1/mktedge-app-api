'''
Custom command for the django application to wait for the database.
8/26/2022

DJacobson
'''

import time

from psycopg2 import OperationalError as Psycopg2Error

from django.core.management.base import BaseCommand
from django.db.utils import OperationalError


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Waiting for db...")
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write('Database is unavailable, trying again in 1 second ...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database is available.'))
