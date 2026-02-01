from django.shortcuts import render, redirect, get_object_or_404
from .forms import GroupForm, Group, CustomUser
from django.http import HttpResponse, JsonResponse
import json
from django.db.models import Count, Q
from.models import StudentGroup
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
    coaches = CustomUser.objects.filter(role="Тренер")
    # .prefetch_related(
    #     'coach_groups__customuser_set'
    # )
    

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

def student(request, pk):
    student_data = get_object_or_404(CustomUser, pk=pk)

    try:
        student_group = student_data.current_groups
        current_group = [{'id':student_group.group.id,'group_name':student_group.group.group_name}] 
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

# Create your views here.
