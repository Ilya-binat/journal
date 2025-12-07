from.views import *
from django.urls import path

urlpatterns =[
    path('create_user/', register, name='create_user'),
    path('group/', group, name = 'group'),
    path('add_group/', add_group, name = 'add_group'),
    path('edit_group/<int:pk>', edit_group, name = 'edit_group'),
    

]