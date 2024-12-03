from django.urls import path, include
from Applications.Order.views import take_order

urlpatterns = [
    path('', take_order, name='take_order'),
]