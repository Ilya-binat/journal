from ..models import *
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import *
from django.http import HttpResponse, JsonResponse

def assessments(request):
    
    data = Assessment.objects.all()

    return render(request,'assessments.html',{'assessments':data})