from django.shortcuts import render, get_object_or_404
from ..forms import *
from django.http import HttpResponse, JsonResponse
from ..models import *

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