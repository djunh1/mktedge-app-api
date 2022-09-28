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
    start_date=models.DateTimeField()
    end_date= models.DateTimeField()
    num_bases=models.IntegerField()
    sector=models.TextField()  #TODO: add choice field?
    length_run=models.IntegerField()
    pct_gain=models.DecimalField(max_digits=7, decimal_places=1)

    def __str__(self):
        return self.ticker
