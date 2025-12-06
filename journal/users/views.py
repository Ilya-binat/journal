from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from django.http import HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required





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


# Create your views here.
