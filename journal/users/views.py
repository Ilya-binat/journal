from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from django.http import HttpResponse
from django.contrib.auth import login, logout

def register(request):
    form = RegisterForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect(request, 'log_in.html', {'form:form'})
    

    return render(request, 'register.html', {'form':form})

def log_in(request):

    form = LoginForm(data=request.POST or None)

    if form.is_valid():
        user = form.get_user()
        login(request,user)

        return redirect('users:home')
    
    return render(request, 'log_in.html', {'form':form})

def log_out(request):
    logout(request)
    return redirect('users:log_in')    

def home(request):
    form = LoginForm()  
    return render(request, 'home.html', {'form': form}) 

# Create your views here.
