from django.urls import path
from .views import *
from . import views

app_name = "main"

urlpatterns = [
    path('', mainpage, name="mainpage"),
    path('weatherpage/', weatherpage, name="weatherpage"),
    path('soilpage/', soilpage, name="soilpage"),
    path('get-sigungu/', views.get_sigungu, name='get_sigungu'),
    path('get-eupmyeondong/', views.get_eupmyeondong, name='get_eupmyeondong'),
]