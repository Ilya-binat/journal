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

    
]