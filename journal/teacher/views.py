from django.shortcuts import render
from .utils import *
from administrator.models import *
from datetime import datetime, date
import json
from django.utils import timezone
from users.decorators import role_required

@role_required('Тренер')
def teacher_schedule(request):
    week_days = get_week_days()
    today = timezone.localdate()
    slots = Slot.objects.filter(date=today, coach=request.user)
    slots_count = slots.count()
    total_duration = count_training_time(request.user) or 0
    trainings = build_schedule_slots(slots) if slots.exists() else []
    week_trainings = get_week_training(request)

    return render(request, 'teacher_schedule.html',
                  {'week_days': week_days,
                   'slots': slots,
                   'slots_count': slots_count,
                   "current_date": date.today(),
                   'total_duration': total_duration,
                   'trainings': trainings,
                   'week_trainings': week_trainings,
                   })

# Create your views here.
