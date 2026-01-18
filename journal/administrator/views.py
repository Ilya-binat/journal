from django.shortcuts import render, redirect, get_object_or_404
from .forms import GroupForm, Group, CustomUser
from django.http import HttpResponse, JsonResponse
import json
from django.db.models import Count, Q

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

    return render(request, "coaches.html", {"coaches": coaches})


def students(request):
    student_list = CustomUser.objects.filter(role="Спортсмен")

    return render(request, "students.html", {"students": student_list})


def coach(request, pk):
    coach_data = get_object_or_404(CustomUser, pk=pk)

    # Получаем список, групп тренера в в виде словарей с id и именем группы.
    coach_groups = list(coach_data.group_set.values("id", "group_name"))
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


# Create your views here.
