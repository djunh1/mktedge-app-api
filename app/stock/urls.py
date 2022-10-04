
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from stock import views

router = DefaultRouter()
router.register('stocks', views.StockViewSet)

app_name = 'stock'

urlpatterns = [
    path('', include(router.urls)),
]


