from.views import *
from django.urls import path



urlpatterns = [
    path('home/', home, name = 'home'),
    path('register/', register, name = 'register'),
    path('log_in/', log_in, name = 'log_in'),
    path('log_out/', log_out, name = 'log_out'),
    path('profile/', profile, name = 'profile'),
    path('profile/update-avatar/', update_avatar, name='update_avatar'), 
    path('profile/edit_profile/', edit_profile, name = 'edit_profile'),
    path('profile/change_password', change_password, name = 'change_password'),
    path('profile/profile_update/', profile_update, name = 'profile_update')
   
]