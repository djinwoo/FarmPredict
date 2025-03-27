from django.urls import path
from .views import *

app_name = "main"

urlpatterns = [
    path('', mainpage, name="mainpage"),
    path('weatherpage/', weatherpage, name="weatherpage"),
    path('soilpage/', soilpage, name="soilpage"),
]