from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_short_url, name='create_short_url'),
    path('check-safety/', views.check_safety_only, name='check_safety_only'),
    path('<str:short_code>/details/', views.link_details, name='link_details'),
    path('<str:short_code>/', views.redirect_url, name='redirect_url'),
]