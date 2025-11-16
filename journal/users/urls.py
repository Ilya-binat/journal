from.views import *
from django.urls import path



urlpatterns = [
    path('register/', register, name = 'register'),
    path('log_in/', log_in, name = 'log_in'),
    path('log_out/', log_out, name = 'log_out')
]