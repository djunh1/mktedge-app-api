'''
DB Models
'''
from django.conf import settings

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

class UserManager(BaseUserManager):
    """Manager for the user"""

    def create_user(self, email, password=None, **extra_field):
        if not email:
            raise ValueError('Email address required for user.')
        user = self.model(email=self.normalize_email(email), **extra_field)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user



class User(AbstractBaseUser, PermissionsMixin):
    """Mkt Edge app system User"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Stock(models.Model):
    """Stock Ticker object.  Each ticker is an individual stock run
    """

    #TODO: Add TextChoices for each sector

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    ) # maybe consider removing the cascaded delete, we want to keep stocks even if user is deleted

    ticker=models.CharField(max_length=10)
    start_date=models.DateField()
    end_date= models.DateField()
    num_bases=models.IntegerField()
    sector=models.TextField()  #TODO: add choice field?
    length_run=models.IntegerField()
    pct_gain=models.DecimalField(max_digits=7, decimal_places=1)
    stock_run_notes = models.TextField(blank=True)

    bases = models.ManyToManyField('StockBase')

    def __str__(self):
        return self.ticker

class StockBase(models.Model):
    """Stock base object.

    price_percent_run - temporarily the movement from bottom of base (first connecting two points),
    to the top (first connecting two points).

    Args:
        models (_type_): _description_
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    stock_reference = models.ForeignKey(
        Stock,
        on_delete=models.PROTECT, null=True
    )

    ticker=models.CharField(max_length=10)

    base_count=models.IntegerField()
    base_failure=models.CharField(max_length=1, null=True)
    bo_date=models.DateField()
    vol_bo=models.IntegerField(blank=True, null=True)
    vol_20=models.IntegerField(blank=True, null=True)
    bo_vol_ratio=models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    price_percent_range=models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    base_length=models.IntegerField(blank=True, null=True)

    #fundies
    sales_0qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    # sales_1qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # sales_2qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # sales_3qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # sales_4qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # sales_5qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # sales_6qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # sales_7qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    # gm_0qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # gm_1qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # gm_2qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # gm_3qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # gm_4qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # gm_5qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # gm_6qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # gm_7qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    # eps_0qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # eps_1qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # eps_2qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # eps_3qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # eps_4qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # eps_5qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # eps_6qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # eps_7qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    # net_margin_0qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # net_margin_1qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # net_margin_2qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # net_margin_3qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # net_margin_4qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # net_margin_5qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # net_margin_6qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # net_margin_7qtr = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    # eps_0qtr_yoy = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # eps_1qtr_yoy = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # eps_2qtr_yoy = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # eps_3qtr_yoy = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    # gm_0qtr_yoy = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # gm_1qtr_yoy = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # gm_2qtr_yoy = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # gm_3qtr_yoy = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    # net_margin_0qtr_yoy = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # net_margin_1qtr_yoy = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # net_margin_2qtr_yoy = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # net_margin_3qtr_yoy = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    # sales_0qtr_yoy = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # sales_1qtr_yoy = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # sales_2qtr_yoy = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # sales_3qtr_yoy = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    def __str__(self):
        return self.ticker

