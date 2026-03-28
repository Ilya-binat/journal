from django.shortcuts import render, get_object_or_404
from ..forms import *
from django.http import JsonResponse
import json
from ..models import *

def students(request):
    student_list = CustomUser.objects.filter(role="Спортсмен")

    return render(request, "students.html", {"students": student_list})


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