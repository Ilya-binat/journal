from.views import *
from django.urls import path

urlpatterns =[
    path('group/', group, name = 'group'),
    path('add_group/', add_group, name = 'add_group'),
    path('edit_group/<int:pk>', edit_group, name = 'edit_group'),
    path('delete_group/<int:pk>', delete_group, name = 'delete_group'),
    path('coaches/', coaches, name = 'coaches'),
    path('delete_coach/<int:pk>', delete_coach, name = 'delete_coach'),
    path('edit_coach/<int:pk>', edit_coach, name = 'edit_coach'),
]