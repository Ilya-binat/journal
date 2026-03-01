from.views import *
from django.urls import path

urlpatterns =[
    path('group/', group, name = 'group'),
    path('add_group/', add_group, name = 'add_group'),
    path('edit_group/<int:pk>', edit_group, name = 'edit_group'),
    path('delete_group/<int:pk>', delete_group, name = 'delete_group'),
    path('coaches/', coaches, name = 'coaches'),
    path('students/', students, name = 'students'),
    path('coach/<int:pk>', coach, name = 'coach'),
    path('save_coach_groups/<int:pk>', save_coach_groups, name = 'save_coach_groups'),
    path('student/<int:pk>', student, name = 'student'),
    path('save_student_group/<int:pk>', save_student_group, name = 'save_student_group'),
    path('delete_student_group/<int:pk>', delete_student_group, name = 'delete_student_group'),
    path('get_students_list/<int:pk>', get_students_list, name = 'get_students_list'),
    path('periods/', periods, name = 'periods'),
    path('add_period/', add_period, name = 'add_period'),
    path('get_period/<int:pk>/',get_period, name='get_period'),
    path('edit_period/<int:pk>/', edit_period, name = 'edit_period'),
    path('delete_period/<int:pk>', delete_period, name = 'delete_period'),
    path('halls/', halls, name = 'halls'),
    path('add_hall/', add_hall, name = 'add_hall'),
    path('get_hall/<int:pk>/', get_hall, name = 'get_hall'),
    path('edit_hall/<int:pk>/', edit_hall, name = 'edit_hall'),
    path('delete_hall/<int:pk>/', delete_hall, name = 'delete_hall'),
    path('schedule/', schedule, name = 'schedule'),
    path('add_schedule/', add_schedule, name = 'add_schedule'),
    path('save_schedule/', save_schedule, name = 'save_schedule'),# Разделение функции охранения на две части 1.Открытие страницы сохранения 2.Само сохранение
]