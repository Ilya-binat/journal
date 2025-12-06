from.views import *
from django.urls import path

urlpatterns =[
    path('create_user/', register, name='create_user'),
]