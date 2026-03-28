from django.shortcuts import render, get_object_or_404
from ..forms import *
from django.http import JsonResponse
import json
from django.db.models import Count
from ..models import *

def coaches(request):
    coaches = CustomUser.objects.filter(role="Тренер").annotate(
        student_count=Count("coach_groups__group_students")
    )

    return render(request, "coaches.html", {"coaches": coaches})


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