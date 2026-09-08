from django.urls import path
from .views import create_short_url, redirect_url

urlpatterns = [
    path('', create_short_url, name='create_short_url'),
    path('<str:short_code>/', redirect_url, name='redirect_url'),
]