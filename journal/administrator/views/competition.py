from ..models import *
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import *
from django.http import HttpResponse, JsonResponse

# Функция вывода соревнований


def competitions(request):
    form = CompetitionForm()
    data = Competition.objects.all()

    return render(request, "competitions.html", {"competitions": data, "form": form})


def add_competition(request):
    form = CompetitionForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        competition = form.save()
        return JsonResponse(
            {
                "success": True,
                "competition": {
                    "id": competition.id,
                    "title": competition.title,
                    "sport_type": competition.sport_type.name,
                    "date_start": competition.date_start,
                    "date_end": competition.date_end,
                    "address": competition.address,
                },
            }
        )

    return JsonResponse({"success": False, "errors": form.errors}, status=400)


def edit_competition(request, pk):
    competition_data = Competition.objects.get(pk=pk)
    form = CompetitionForm(request.POST or None, instance=competition_data)

    if request.method == "POST" and form.is_valid():
        competition = form.save()
        return JsonResponse(
            {
                "success": True,
                "competition": {
                    "id": competition.id,
                    "title": competition.title,
                    "sport_type": competition.sport_type.name,
                    "address": competition.address,
                    "date_start": competition.date_start,
                    "date_end": competition.date_end,
                },
            }
        )
    return JsonResponse({"success": False, "errors": form.errors}, status=400)


def get_competition(request, pk):
    competition = get_object_or_404(Competition, pk=pk)

    return JsonResponse(
        {
            "id": competition.id,
            "title": competition.title,
            "sport_type": competition.sport_type.id,
            "address": competition.address,
            "date_start": competition.date_start,
            "date_end": competition.date_end,
        }
    )
