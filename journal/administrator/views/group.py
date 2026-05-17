from django.shortcuts import render, redirect
from ..forms import *
from django.http import HttpResponse
from ..models import *
from users.decorators import role_required

@role_required('Администратор')
def group(request):
    groups = Group.objects.all()
    return render(request, "group.html", {"groups": groups})

@role_required('Администратор')
def add_group(request):
    form = GroupForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("administrator:group")
    return render(request, "add_group.html", {"form": form})

@role_required('Администратор')
def edit_group(request, pk):
    group_data = Group.objects.get(pk=pk)
    form = GroupForm(
        request.POST or None, instance=group_data
    )  # Заполняем форму и передаем ее в шаблон
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("administrator:group")
    return render(request, "add_group.html", {"form": form})

@role_required('Администратор')
def delete_group(request, pk):
    group_data = Group.objects.get(pk=pk)
    if request.method == "POST":
        group_data.delete()
    return HttpResponse()