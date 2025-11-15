from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.http import HttpResponse

def register(request):
    form = RegisterForm(request.POST or None)

    if form.is_valid():
        form.save()
        return HttpResponse('Регистрация прошла успешно')
    

    return render(request, 'register.html', {'form':form})
# Create your views here.
