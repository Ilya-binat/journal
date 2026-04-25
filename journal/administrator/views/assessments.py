from ..models import *
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import *
from django.http import HttpResponse, JsonResponse


def assessments(request):
    form = AssessmentForm()
    data = Assessment.objects.all()

    return render(request, "assessments.html", {"assessments": data, "form": form})


def add_assessment(request):
    form = AssessmentForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        assessment = form.save()
        return JsonResponse(
            {
                "success": True,
                "assessment": {
                    "id": assessment.id,
                    "name": assessment.name,
                    "coach": assessment.coach.get_short_name(),
                    "group": assessment.group.group_name,
                    "sport_type": (
                        assessment.sport_type.name if assessment.sport_type else None
                    ),
                    "date_start": assessment.date_start.strftime("%Y-%m-%d"),
                    "date_end": assessment.date_end.strftime("%Y-%m-%d"),
                },
            }
        )

    return JsonResponse({"success": False, "errors": form.errors}, status=400)


def get_assessment(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk)

    return JsonResponse(
        {
            "id": assessment.id,
            "name": assessment.name,
            "coach": assessment.coach.id,
            "group": assessment.group.id,
            "sport_type": (
                assessment.sport_type.id if assessment.sport_type else None
            ),
            "date_start": assessment.date_start,
            "date_end": assessment.date_end,
        }
    )

def edit_assessment(request, pk):
    assessment_data = Assessment.objects.get(pk=pk)
    form = AssessmentForm(request.POST or None, instance=assessment_data)

    if request.method == "POST" and form.is_valid():
        assessment = form.save()
        return JsonResponse(
            {
                "success": True,
                "assessment": {
                    "id": assessment.id,
                    "name": assessment.name,
                    "coach": assessment.coach.get_short_name(),
                    "group": assessment.group.group_name,
                    "sport_type": assessment.sport_type.name,
                    "date_start": assessment.date_start,
                    "date_end": assessment.date_end,
                },
            }
        )
    return JsonResponse({"success": False, "errors": form.errors}, status=400)

def delete_assessment(request, pk):
    assessment_data = Assessment.objects.get(pk=pk)
    if request.method == 'POST':
        assessment_data.delete()

        return HttpResponse()