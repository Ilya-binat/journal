from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    ROLE_CHOICES = [
        ("Спортсмен", "Спортсмен"),
        ("Тренер", "Тренер"),
        ("Администратор", "Администратор"),
    ]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=255, choices=ROLE_CHOICES)
    middle_name = models.CharField(
        max_length=255, null=True, blank=True
    )  # null=True, blank=True - Делают поля не обязательными для заполнения
    birth_date = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=11, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def get_full_name(self): # Соединение полей ФИО в одно. Далее в html меняем на эту функцию
        full_name = "%s %s %s" % (self.last_name, self.first_name, self.middle_name)
        return full_name.strip() #strip - удаление пробеллов по бокам



# Create your models here.
