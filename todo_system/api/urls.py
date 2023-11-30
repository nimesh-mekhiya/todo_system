# accounts/urls.py

from django.urls import path
from .views import RegisterAPI, LoginAPI
urlpatterns = [
    path('api/register/', RegisterAPI.as_view(), name='register'),
    path('api/login/', LoginAPI.as_view(), name='login'),
]