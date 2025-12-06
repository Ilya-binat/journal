from django.shortcuts import render, redirect
from .forms import RegisterForm
from django .http import HttpResponse



def register(request):
    if not request.user.is_superuser:
        return HttpResponse('Извиниет у Вас нет прав для выполнения этого действия')
    
    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)  # не сохраняем сразу
        user.username = form.cleaned_data["email"]  # подставляем email
        user.set_password ('12345678')
        user.save()  # теперь сохраняем
        return redirect("users:log_in")  # переход на логин-страницу

    return render(request, "register.html", {"form": form})
# Create your views here.
