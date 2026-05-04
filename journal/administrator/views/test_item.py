from ..models import *
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import *
from django.http import HttpResponse, JsonResponse

def test_items(request):
    data = TestItem.objects.all()
    form = TestItemForm()

    return render(
        request,
        'test_items.html',
        {
            'data': data,
            'form': form
        }
    )

def add_test_items(request):
    form = TestItemForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        test = form.save()
        return JsonResponse(
            {
                "success": True,
                "test": {
                    "id": test.id,
                    "name": test.name,
                    "stage": test.stage,
                    "max_cor_male":test.max_cor_male,
                    "max_cor_female":test.max_cor_female
                    }

            }
        )
    return JsonResponse({"success": False, "errors": form.errors}, status=400)

def get_test_items(request, pk):
    test = get_object_or_404(Assessment, pk=pk)

    return JsonResponse(
        {
            "id": test.id,
            "name": test.name,
            "stage":test.stage,
            "max_cor_male":test.max_cor_male,
            "max_cor_female":test.max_cor_female
        }
    )