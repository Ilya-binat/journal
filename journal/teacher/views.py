from django.shortcuts import render
from .utils import *

def teacher_schedule(request):
    week_days = get_week_days()
    return render(request, 'teacher_schedule.html', {'week_days':week_days})


# Create your views here.
