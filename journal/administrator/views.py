from django.shortcuts import render, redirect
from .forms import RegisterForm, GroupForm, Group
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

def group(request):
    groups = Group.objects.all()
    return render(request, 'group.html', {"groups":groups})


def add_group(request):
    form = GroupForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('administrator:group')
    return render(request, 'add_group.html', {"form": form})

def edit_group(request, pk):
    group_data = Group.objects.get(pk=pk)
    form = GroupForm(request.POST or None, instance=group_data)# Заполняем форму и передаем ее в шаблон
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('administrator:group')
    return render(request, 'add_group.html', {"form":form})
# Create your views here.
