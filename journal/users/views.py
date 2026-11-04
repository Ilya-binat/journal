from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import *
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .models import *
import json


def register(request):
    if not request.user.is_superuser:
        return HttpResponse('Извиниет у Вас нет прав для выполнения этого действия')

    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)  # не сохраняем сразу
        user.username = form.cleaned_data["email"]  # подставляем email
        user.set_password('12345678')
        user.save()  # теперь сохраняем
        return redirect("users:users")  # переход на страницу пользователей

    return render(request, "register.html", {"form": form})


def log_in(request):
    form = LoginForm(data=request.POST or None)
    print(f"is_valid: {form.is_valid()}")
    print(f"errors: {form.errors}")

    if form.is_valid():
        user = form.get_user()
        if user is not None:
            login(request, user)
            print(f"role: '{user.role}'")
            if user.role == 'Администратор':
                return redirect("administrator:schedule")
            elif user.role == 'Тренер':
                return redirect("teacher:schedule")
            elif user.role == 'Спортсмен':
                return redirect('student:schedule')
            else:
                print("Роль не совпала ни с одним условием!")

    return render(request, "log_in.html", {"form": form})


def log_out(request):
    logout(request)
    return redirect("users:log_in")


@login_required(login_url='/users/log_in')  # нужно импортировать login_required
def profile(request):
    return render(request, "profile.html", {"user_obj": request.user})


# Функция смены аватарки
@login_required(login_url='/users/log_in')
@require_POST
def update_avatar(request):
    form = AvatarForm(request.POST, request.FILES)

    if form.is_valid():
        user = request.user
        if user.avatar:
            user.avatar.delete(save=False)
        user.avatar = form.cleaned_data.get('avatar')
        user.save(update_fields=[
            'avatar'])  # update_fields - принимает только массив поэтому обращаемся к полю avatar черз массив
        messages.success(request, 'Фото обнавлено')
    else:
        messages.error(request, form.errors['avatar'][
            0])  # form.errors словарь-Сохраняет виды ошибок в словаре со значением в виде массива.

    return redirect('users:profile')


# Функция удаления аватарки
@login_required(login_url='/user/log_in')
@require_POST
def delete_avatar(request):
    user = request.user

    if user.avatar:
        user.avatar.delete(save=False)
        user.avatar = None
        user.save(update_fields=['avatar'])
        messages.success(request, 'Фото удалено')

    return redirect('users:profile')


#

# Функция редактирования профайла пользователя
@login_required(login_url='/users/log_in')
def edit_profile(request):
    user = CustomUser.objects.get(pk=request.user.pk)
    form = ProfileForm(request.POST or None,
                       instance=user)  # instance - нужен для того что бы показать информацию профиля в форме

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Профиль обнавлен')

    return redirect('users:profile')


# Смена пароля
@login_required(login_url='/users/log_in')
def change_password(request):
    form = StyledPasswordChangeForm(request.user, request.POST or None)

    if request.methood == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Пароль обнавлен')
        return redirect('users:profile')

    return render(request, 'change_password.html', {'form': form})


@login_required(login_url='/users/log_in')
@require_POST
def change_user_password(request, pk):
    if request.user.role != 'Администратор' and not request.user.is_superuser:
        return JsonResponse({
            'success': False,
            'error': 'Не достаточно прав'
        }, status=403)
    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponse({
            'success': False,
            'error': 'Не корректный запрос'
        }, status=400)

    password1 = data.get('password1') or ''
    password2 = data.get('password2') or ''

    if len(password1) < 8:
        return JsonResponse({
            'success': False,
            'error': 'Пароль слишком короткий',

        }, status=400)

    if password1 != password2:
        return JsonResponse({
            'success': False,
            'error': 'Пароли не совпадают'
        }, status=400)

    target = get_object_or_404(CustomUser, pk=pk)
    target.set_pasword(password1)
    target.save()
    if target.pk == request.user.pk:
        update_session_auth_hash(request, target)
    return JsonResponse({
        'success': True
    })




@login_required(login_url='/users/log_in')
@require_POST
def profile_update(request):
    form = PhoneForm(request.POST)

    if form.is_valid():
        request.user.phone_number = form.cleaned_data.get('phone_number')
        request.user.save(update_fields=['phone_number'])
        messages.success(request, 'Телефон сохранен' if request.user.phone_number else 'Телефон удален')
    else:
        messages.error(request, form.errors['phone_number'][0])

    return redirect('users:profile')


def users(request):
    users = CustomUser.objects.filter(is_superuser=False)

    return render(request, 'users.html', {'users': users})


@login_required(login_url='/users/log_in')
def edit_user(request, pk):
    user = CustomUser.objects.get(pk=pk)
    form = RegisterForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('users:users')
    return render(request, 'register.html', {'form': form})


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

    if len(password1) < 8:
        return JsonResponse('Пароль слишком короткий')

    if password1 != password2:
        return JsonResponse('Пароли не совпадают')

    user = request.user
    user.set_password(password1)
    user.save()
    update_session_auth_hash(request, user)

    return HttpResponse('Смена пароля')


def get_401(request):
    return render(request, '401.html')


def get_403(request):
    return render(request, '403.html')
