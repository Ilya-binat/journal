from django.shortcuts import render, redirect
from .forms import LoginForm, RegisterForm
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from.models import *
import json


def register(request):
    if not request.user.is_superuser:
        return HttpResponse('Извиниет у Вас нет прав для выполнения этого действия')
    
    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)  # не сохраняем сразу
        user.username = form.cleaned_data["email"]  # подставляем email
        user.set_password ('12345678')
        user.save()  # теперь сохраняем
        return redirect("users:users")  # переход на страницу пользователей

    return render(request, "register.html", {"form": form})


def log_in(request):

    form = LoginForm(data=request.POST or None)

    if form.is_valid():
        user = form.get_user()
        login(request, user)

        return redirect("student:schedule")

    return render(request, "log_in.html", {"form": form})


def log_out(request):
    logout(request)
    return redirect("users:log_in")


@login_required(login_url='/users/log_in')  # нужно импортировать login_required
def profile(request):
    return render(request, "profile.html", {"user_obj": request.user})


@login_required(login_url='/users/log_in')
def update_avatar(request):
    if request.method == "POST":
        avatar = request.FILES.get("avatar")
        if avatar:
            request.user.profile.image = avatar
            request.user.profile.save()
        return redirect("users:profile")

    return redirect("users:profile")


@login_required(login_url='/users/log_in')
def edit_profile(request):
    return render(request, "edit_profile.html")


@login_required(login_url='/users/log_in')
def change_password(request):
    return render(request, "change_password.html")


@login_required(login_url='/users/log_in')
def profile_update(request):
    return render(request, "profile_update.html")

def users(request):
    users = CustomUser.objects.filter(is_superuser = False)

    return render(request, 'users.html', {'users':users})

@login_required(login_url='/users/log_in')
def edit_user(request, pk):
    user = CustomUser.objects.get(pk=pk)
    form = RegisterForm(request.POST or None, instance = user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('users:users')
    return render(request, 'register.html', {'form':form})

@login_required(login_url='/users/log_in')
def delete_user(request, pk):
    user_data = CustomUser.objects.get(pk=pk)
    if request.method == 'POST':
        user_data.delete()
    return redirect('users:users')

@login_required(login_url='/users/log_in')
def patch_user(request, pk):
    user = CustomUser.objects.get(pk=pk)
    user.is_active = not user.is_active
    user.save()
    
    return redirect('users:users')

@login_required(login_url='/users/log_in')
def change_password(request, pk):
    data = json.loads(request.body)
    password1 = data.get('password1')
    password2 = data.get('password2')

    if len (password1) < 8:
        return JsonResponse('Пароль слишком короткий')
    
    if password1 != password2:
        return JsonResponse('Пароли не совпадают')
    
    user = request.user
    user.set_password(password1)
    user.save()
    update_session_auth_hash(request, user)

    return HttpResponse('Смена пароля')

