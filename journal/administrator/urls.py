from.views import *
from django.urls import path

urlpatterns =[
    path('create_user/', register, name='create_user'),
    path('group/', group, name = 'group'),
    path('add_group/', add_group, name = 'add_group'),
    path('edit_group/<int:pk>', edit_group, name = 'edit_group'),
    path('delete_group/<int:pk>', delete_group, name = 'delete_group'),
    path('users/', users, name = 'users'),
    path('edit_user/<int:pk>', edit_user, name = 'edit_user'),
    

]