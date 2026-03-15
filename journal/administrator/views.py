from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django.http import HttpResponse, JsonResponse
import json
from django.db.models import Count, Q
from .models import *
from users.forms import RegisterForm


def group(request):
    groups = Group.objects.all()
    return render(request, "group.html", {"groups": groups})


def add_group(request):
    form = GroupForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("administrator:group")
    return render(request, "add_group.html", {"form": form})


def edit_group(request, pk):
    group_data = Group.objects.get(pk=pk)
    form = GroupForm(
        request.POST or None, instance=group_data
    )  # Заполняем форму и передаем ее в шаблон
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("administrator:group")
    return render(request, "add_group.html", {"form": form})


def delete_group(request, pk):
    group_data = Group.objects.get(pk=pk)
    if request.method == "POST":
        group_data.delete()
    return HttpResponse()


def coaches(request):
    coaches = CustomUser.objects.filter(role="Тренер").annotate(
        student_count=Count("coach_groups__group_students")
    )

    return render(request, "coaches.html", {"coaches": coaches})


def students(request):
    student_list = CustomUser.objects.filter(role="Спортсмен")

    return render(request, "students.html", {"students": student_list})


def coach(request, pk):
    coach_data = get_object_or_404(CustomUser, pk=pk)

    # Получаем список, групп тренера в виде словарей с id и именем группы.
    coach_groups = list(coach_data.coach_groups.values("id", "group_name"))
    all_groups = list(Group.objects.values("id", "group_name"))

    return JsonResponse(
        {
            "coach_id": coach_data.id,
            "coach_groups": coach_groups,
            "all_groups": all_groups,
            "coach_name": coach_data.get_full_name(),
        }
    )


def save_coach_groups(request, pk):
    # Находим трнера
    coach = get_object_or_404(CustomUser, pk=pk)

    # json строку превращаем в python словарь, чтобы
    # можно было достать информацию
    data = json.loads(request.body)

    # Достаем из словаря все id группы
    groups_id = data.get("groups")

    # Убираем тренера у всех его групп
    Group.objects.filter(coach=coach).update(coach=None)

    # Находим все выбранные группы и назначаем им тренера
    Group.objects.filter(id__in=groups_id).update(coach=coach)

    # Передаем команду, действие выполнено успешно
    return JsonResponse({"status": "ok"})


# Отвечает за открытие модального окна и вывода информации и показ группы к которой студент прикреплен
def student(request, pk):
    student_data = get_object_or_404(CustomUser, pk=pk)

    try:
        student_group = student_data.current_groups
        current_group = [
            {"id": student_group.group.id, "group_name": student_group.group.group_name}
        ]
    except StudentGroup.DoesNotExist:
        current_group = []

    all_groups = list(Group.objects.values("id", "group_name"))

    return JsonResponse(
        {
            "student_id": student_data.id,
            "current_group": current_group,
            "all_groups": all_groups,
        }
    )


def save_student_group(request, pk):

    student = get_object_or_404(CustomUser, pk=pk)

    data = json.loads(request.body)

    group_id = data.get("group")[0]

    student_group = StudentGroup.objects.filter(student=student).exists()
    if student_group:
        StudentGroup.objects.filter(student=student).update(group=group_id)
    else:
        group = get_object_or_404(Group, pk=group_id)
        StudentGroup.objects.create(student=student, group=group)

    return JsonResponse({"status": "ok"})


def delete_student_group(request, pk):

    student_group = get_object_or_404(StudentGroup, pk=pk)

    if request.method == "POST":
        student_group.delete()

    return JsonResponse({"status": "ok"})


def get_students_list(request, pk):
    group = Group.objects.get(pk=pk)

    student_list = group.group_students.all()

    response = []

    for student_group in student_list:
        response.append(
            {
                "id": student_group.student.id,
                "full_name": student_group.student.get_full_name(),
            }
        )

    response = sorted(
        response, key=lambda x: x["full_name"]
    )  # Сортировка списа студентов по имени

    return JsonResponse({"students": response, "group_name": group.group_name})


def periods(request):
    form = PeriodForm()
    periods = SchedulePeriod.objects.order_by(
        "date_start"
    )  # по дате начала по возрастанию
    return render(request, "periods.html", {"form": form, "periods": periods})


def add_period(request):
    form = PeriodForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        period = form.save()
        return JsonResponse(
            {
                "success": True,
                "period": {
                    "id": period.id,
                    "name": period.name,
                    "date_start": period.date_start.strftime("%Y-%m-%d"),
                    "date_end": period.date_end.strftime("%Y-%m-%d"),
                },
            }
        )

    return JsonResponse({"success": False, "errors": form.errors}, status=400)


def delete_period(request, pk):
    data_period = SchedulePeriod.objects.get(pk=pk)
    if request.method == "POST":
        data_period.delete()
    return HttpResponse()


# Берем период который будет редактироваться
def get_period(request, pk):
    period = get_object_or_404(SchedulePeriod, pk=pk)

    return JsonResponse(
        {
            "id": period.id,
            "name": period.name,
            "date_start": period.date_start.strftime("%Y-%m-%d"),
            "date_end": period.date_end.strftime("%Y-%m-%d"),
        }
    )


def edit_period(request, pk):
    period_data = SchedulePeriod.objects.get(pk=pk)
    form = PeriodForm(request.POST or None, instance=period_data)

    if request.method == "POST" and form.is_valid():
        period = form.save()
        return JsonResponse(
            {
                "success": True,
                "period": {
                    "id": period.id,
                    "name": period.name,
                    "date_start": period.date_start.strftime("%Y-%m-%d"),
                    "date_end": period.date_end.strftime("%Y-%m-%d"),
                },
            }
        )
    return JsonResponse({"success": False, "errors": form.errors}, status=400)


# CRUD - зал
def halls(request):
    form = HallForm()
    halls = Hall.objects.order_by("hall_name")  # по дате начала по возрастанию
    return render(request, "halls.html", {"form": form, "halls": halls})


def add_hall(request):
    form = HallForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        hall = form.save()
        return JsonResponse(
            {
                "success": True,
                "hall": {
                    "id": hall.id,
                    "hall_name": hall.hall_name,
                    "training_type": hall.training_type.name,
                },
            }
        )

    return JsonResponse({"success": False, "errors": form.errors}, status=400)


def delete_hall(request, pk):
    data_hall = Hall.objects.get(pk=pk)
    if request.method == "POST":
        data_hall.delete()
    return HttpResponse()


# Берем зал который будет редактироваться
def get_hall(request, pk):
    hall = get_object_or_404(Hall, pk=pk)

    return JsonResponse(
        {
            "id": hall.id,
            "hall_name": hall.hall_name,
            "training_type": hall.training_type.id,
        }
    )


def edit_hall(request, pk):
    hall_data = Hall.objects.get(pk=pk)
    form = HallForm(request.POST or None, instance=hall_data)

    if request.method == "POST" and form.is_valid():
        hall = form.save()
        return JsonResponse(
            {
                "success": True,
                "hall": {
                    "id": hall.id,
                    "hall_name": hall.hall_name,
                    "training_type": hall.training_type.name,
                },
            }
        )
    return JsonResponse({"success": False, "errors": form.errors}, status=400)


# Расписание


def schedule(request):
    schedules = Schedule.objects.all()

    return render(request, "schedule.html", {"schedules": schedules})


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
    coaches = CustomUser.objects.filter(role="Тренер")
    all_groups = Group.objects.all()
    halls = Hall.objects.all()
    periods = SchedulePeriod.objects.all()
    weekdays = WeekDay.objects.all()

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

            return redirect("administrator:schedule")
        
        return render(
            request,
            "add_schedule.html",
            {
                "coaches": coaches,
                "all_groups": all_groups,
                "halls": halls,
                "periods": periods,
                "weekdays": weekdays,
                "form": form,
            },
        )


def fetch_coach_groups(request, pk):
    groups = Group.objects.filter(coach_id=pk).values()

    return JsonResponse({"groups": list(groups)})


def delete_schedule(request, pk):
    schedule = Schedule.objects.get(pk=pk)

    if request.method == "POST":
        schedule.delete()

        return JsonResponse({"success": True})


def edit_schedule(request, pk):
    schedule_data = Schedule.objects.get(pk=pk)
    coach_id = schedule_data.coach.id
    group_data = schedule_data.group
    hall_id = schedule_data.hall.id
    period_id = schedule_data.period.id
    weekdays_id = list(schedule_data.weekdays.values_list('id', flat=True))
    start_time = schedule_data.start_time
    end_time = schedule_data.end_time

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

def update_schedule(request, pk):
    schedule_data = get_object_or_404(Schedule, pk=pk)
    coaches = CustomUser.objects.filter(role="Тренер")
    all_groups = Group.objects.all()
    halls = Hall.objects.all()
    periods = SchedulePeriod.objects.all()
    weekdays = WeekDay.objects.all()

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

            return redirect("administrator:schedule")
        
        return render(
            request,
            "edit_schedule.html",
            {
                "schedule_id":schedule_data.id,
                "coaches": coaches,
                "all_groups": all_groups,
                "halls": halls,
                "periods": periods,
                "weekdays": weekdays,
                "form": form,
            },
        )