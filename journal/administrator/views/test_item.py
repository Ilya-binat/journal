from ..models import *
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import *
from django.http import HttpResponse, JsonResponse

def test_items(request):
    data = TestItem.objects.all()

    return render(request, 'test_items.html', {'data':data})