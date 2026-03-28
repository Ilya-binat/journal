# Функции помощники
from datetime import date, timedelta
from .models import Slot

# Создает тренировки при создании расписания 
def generate_slots(schedule):
    period = schedule.period
    weekday_numbers = list(schedule.weekdays.values_list('id', flat = True))
    current = period.date_start

    while current <= period.date_end:
        if current.isoweekday() in weekday_numbers:
            Slot.objects.create(
                date = current, 
                start_time = schedule.start_time,
                end_time = schedule.end_time,
                coach = schedule.coach,
                hall = schedule.hall,
                group = schedule.group
            )
        current += timedelta(days=1)
