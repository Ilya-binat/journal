from datetime import date, timedelta, datetime
from django.utils.formats import date_format
from django.db.models import F, Sum, ExpressionWrapper, DurationField
from administrator.models import Slot


def get_week_days():
    today = date.today()
    monday = today - timedelta(days=today.weekday())

    week_days = []

    for i in range(7):
        day_date = monday + timedelta(days=i)

        week_days.append(
            {
                "date": day_date,
                "day": day_date.day,
                "month": date_format(day_date, "F"),  # май
                "weekday": date_format(day_date, "D"),  # пн, вт
                "weekday_full": date_format(day_date, "l"),  # понедельник
                "is_today": day_date == today,
            }
        )

    return week_days


# Функция для подсчета нагрузки на неделю
def count_training_time(coach):
    week_number = datetime.now().isocalendar()[1]
    total_duration = Slot.objects.filter(date__week=week_number, coach = coach).aggregate(
        total=Sum(
            ExpressionWrapper(
                F("end_time") - F("start_time"), output_field=DurationField()
            )
        )
    )["total"]
    total_seconds = total_duration.total_seconds()

    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)

    result = f"{hours} часов {minutes} минут"

    return result

#  Функция создания сетки тренировок

def build_schedule_slots(trainings):
    ordered_trainings = list(trainings.order_by('start_time'))
    
    if not ordered_trainings:
        return []
    
    slots = []
    cursor = time_to_mins(ordered_trainings[0].start_time)

    for training in ordered_trainings:
        training_start = time_to_mins(training.start_time)
        training_end = time_to_mins(training.end_time)

        if training_start > cursor:
            free_time = training_start - cursor
            slots.append({
                'type':'free',
                'start_time':mins_to_time(cursor),
                'end_time':training.start_time,
                'duration_label':format_duration(free_time)
            })
        busy_time = training_end - training_start
        slots.append({
            'type':'busy',
            'training':training,
            'duration_label':format_duration(busy_time)
        })
        cursor = training_end
    return slots        

# Переводим часы в минуты  
def time_to_mins(t):
    return t.hour * 60 + t.minute

# Переводим минуты в часы 
def mins_to_time(mins):
    return datetime.strptime(f'{mins // 60:02d}:{mins % 60:02d}', '%H:%M').time()
 
# Общая продлжительность тренировки
def format_duration(m):
    if m < 60:
        return f'{m} мин.'
    hours,minutes = divmod(m,60)

    return f'{hours} ч.{minutes} мин.'
    

