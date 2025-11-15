from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser (AbstractUser):
    SPORTSMEN = 'sportsmen'
    COACH = 'coach'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (SPORTSMEN, 'Спортсмен'),
        (COACH, 'Тренер'),
        (ADMIN, 'Администратор')
    ]
    role = models.CharField(max_length=255,choices=ROLE_CHOICES)
    middle_name = models.CharField(max_length=255, null=True, blank=True)# null=True, blank=True - Делают поля не обязательными для заполнения
    birth_date = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=11, null=True, blank=True)
    
# Create your models here.
