from.views import *
from django.urls import path

urlpatterns = [
        path('schedule/', schedule, name ='schedule'),
        
]