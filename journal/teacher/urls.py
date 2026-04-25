from django.urls import path
from.views import *

urlpatterns = [
    path('schedule/', teacher_schedule, name= 'schedule')

]