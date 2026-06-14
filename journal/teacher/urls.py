from django.urls import path
from .views import *

urlpatterns = [
    path('schedule/', teacher_schedule, name='schedule'),
    path('mark_attendance/<int:slot_id>', mark_attendance, name='mark_attendance'),
    path('save_slot_notes/<int:slot_id>', save_slot_notes, name="save_slot_notes"),
    path('save_attendance/<int:slot_id>', save_all_attendance, name='save_all_attendance'),
    path('attendance_report/', attendance_report, name = 'attendance_report'),
]
