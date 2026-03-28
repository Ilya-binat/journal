from django.shortcuts import render, get_object_or_404
from ..forms import *
from django.http import HttpResponse, JsonResponse
from ..models import *

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