from django.shortcuts import render, redirect
from .forms import GroupForm, Group, CustomUser
from django .http import HttpResponse
from users.forms import RegisterForm


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

def delete_group(request, pk):
    group_data = Group.objects.get(pk=pk)
    if request.method == 'POST':
        group_data.delete()
    return HttpResponse()
        
def coaches(request):
    coaches = CustomUser.objects.all()

    return render(request, 'coaches.html', {'coaches':coaches})

def delete_coach(request, pk):
    coach_data = CustomUser.objects.get(pk=pk)
    if request.method == 'POST':
        coach_data.delete()
        return HttpResponse()
    
def edit_coach(request, pk):
    coach = CustomUser.objects.get(pk=pk)
    form = RegisterForm(request.POST or None, instance = coach)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('administrator:coaches')
    return render(request, 'register.html', {'form':form})

# Create your views here.
