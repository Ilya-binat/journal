from.views import *
from django.urls import path



urlpatterns = [
    path('register/', register, name = 'register')
]