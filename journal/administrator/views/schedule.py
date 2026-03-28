from django.shortcuts import render, redirect, get_object_or_404
from ..forms import *
from django.http import JsonResponse
from ..models import *
from ..helper import generate_slots

# Расписание

# Функция выводящая список всех расписаний
def schedule(request):
    schedules = Schedule.objects.all()

    return render(request, "schedule.html", {"schedules": schedules})

# Функция открытия страницы для добавления нового расписания 
def add_schedule(request):
    coaches = CustomUser.objects.filter(role="Тренер")
    all_groups = Group.objects.all()
    halls = Hall.objects.all()
    periods = SchedulePeriod.objects.all()
    weekdays = WeekDay.objects.all()

    return render(
        request,
        "add_schedule.html",
        {
            "coaches": coaches,
            "all_groups": all_groups,
            "halls": halls,
            "periods": periods,
            "weekdays": weekdays,
        },
    )


# Функция сохранения созданного расписания


def save_schedule(request):

    if request.method == "POST":
        form = ScheduleForm(request.POST)

        if form.is_valid():
            coach_id = request.POST.get("coach")
            group_id = request.POST.get("group")
            hall_id = request.POST.get("hall")
            period_id = request.POST.get("period")
            start_time = request.POST.get("start_time")
            end_time = request.POST.get("end_time")
            weekdays = request.POST.getlist("weekdays")

            schedule = Schedule.objects.create(
                coach_id=coach_id,
                group_id=group_id,
                hall_id=hall_id,
                period_id=period_id,
                start_time=start_time,
                end_time=end_time,
            )
            schedule.weekdays.set(weekdays)
            generate_slots(schedule)

            return redirect("administrator:schedule")
        
        return redirect('administrator:add_schedule')

# Выбор тренера и после выбора тренера показываем группы 
def fetch_coach_groups(request, pk):
    groups = Group.objects.filter(coach_id=pk).values()

    return JsonResponse({"groups": list(groups)})

# Функция удвленеия расписания
def delete_schedule(request, pk):
    schedule = Schedule.objects.get(pk=pk)

    if request.method == "POST":
        schedule.delete()

        return JsonResponse({"success": True})

# Функции для редактирования расписания 
def edit_schedule(request, pk):
    # Вывод старой информации
    schedule_data = Schedule.objects.get(pk=pk)
    coach_id = schedule_data.coach.id
    group_data = schedule_data.group
    hall_id = schedule_data.hall.id
    period_id = schedule_data.period.id
    weekdays_id = list(schedule_data.weekdays.values_list('id', flat=True))
    start_time = schedule_data.start_time
    end_time = schedule_data.end_time

    # Показывае всю информцию для редактирования
    coaches = CustomUser.objects.filter(role="Тренер")
    all_groups = Group.objects.all()
    halls = Hall.objects.all()
    periods = SchedulePeriod.objects.all()
    weekdays = WeekDay.objects.all()
    
    return render(
        request,
        "edit_schedule.html",
        {
            "schedule_id":schedule_data.id,
            "coach_id": coach_id,
            "group_data": group_data,
            "hall_id": hall_id,
            "period_id": period_id,
            "weekdays_id": weekdays_id,
            'coaches':coaches,
            'all_groups':all_groups,
            'halls':halls,
            'periods':periods,
            'weekdays':weekdays, 
            'start_time':start_time,
            'end_time':end_time
        },
    )

#  Функция которая сохраняет измения в расписании 
def update_schedule(request, pk):
    schedule_data = get_object_or_404(Schedule, pk=pk)

    if request.method == "POST":
        form = ScheduleForm(request.POST, exclude_pk=schedule_data.pk)

        if form.is_valid():
            schedule_data.coach_id = request.POST.get("coach")
            schedule_data.group_id = request.POST.get("group")
            schedule_data.hall_id = request.POST.get("hall")
            schedule_data.period_id = request.POST.get("period")
            schedule_data.start_time = request.POST.get("start_time")
            schedule_data.end_time = request.POST.get("end_time")
            schedule_data.save()
            selected_weekdays = request.POST.getlist("weekdays")
            schedule_data.weekdays.set(selected_weekdays)

            generate_slots(schedule_data)

            return redirect("administrator:schedule")
        
        return redirect('administrator:edit_schedule')
    
