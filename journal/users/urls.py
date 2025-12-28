from.views import *
from django.urls import path



urlpatterns = [
    path('log_in/', log_in, name = 'log_in'),
    path('log_out/', log_out, name = 'log_out'),
    path('profile/', profile, name = 'profile'),
    path('profile/update-avatar/', update_avatar, name='update_avatar'), 
    path('profile/edit_profile/', edit_profile, name = 'edit_profile'),
    path('profile/change_password', change_password, name = 'change_password'),
    path('profile/profile_update/', profile_update, name = 'profile_update'),
    path('create_user/', register, name='create_user'),
    path('edit_user/<int:pk>', edit_user, name = 'edit_user'),
    path('delete_user/<int:pk>', delete_user, name = 'delete_user'),
    path('patch_user/<int:pk>', patch_user, name = 'patch_user'),# patch - не большое обновление данных пользователя
    path('index/', users, name = 'users'),
    path('change_password/<int:pk>', change_password, name = 'change_password'),
]