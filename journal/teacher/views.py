from django.shortcuts import render
from .utils import *
from administrator .models import *
from datetime import datetime, date
import json 

def teacher_schedule(request):
    week_days = get_week_days()
    slots = Slot.objects.filter(date = datetime.now(), coach = request.user)
    slots_count = len(slots)
    total_duration = count_training_time(request.user)
    trainings = build_schedule_slots(slots)
    

    return render(request, 'teacher_schedule.html', 
                  {'week_days':week_days, 
                  'slots':slots, 
                  'slots_count':slots_count,
                  "current_date": date.today(),
                  'total_duration':total_duration,
                  'trainings':trainings,
                  })


# Create your views here.
