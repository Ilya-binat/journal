from django.db import models

class Coach(models.Model):
    first_name = models.CharField(max_length=255)
    last_name  = models.CharField(max_length=255)
    middle_name  = models.CharField(max_length=255)

class TrainingType(models.Model):
    name = models.CharField(max_length=255)

class Hall(models.Model):
    hall_name = models.CharField(max_length=255)
    training_type = models.ForeignKey('administrator.TrainingType', on_delete=models.SET_NULL, null=True, blank=True)#on_delet=models.SET_NULL - при удаление вида спорта не будет удален зал, а тип спорта станет нулевым.

class Slot(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    coach = models.ForeignKey('administrator.Coach', on_delete=models.SET_NULL, null=True, blank=True)
    hall = models.ForeignKey('administrator.Hall', on_delete=models.SET_NULL, null=True, blank=True)
    group = models.ForeignKey('administrator.Group', on_delete=models.SET_NULL, null=True, blank=True)

stage_choices = [
    ('1', 'НП1'),
    ('2', 'НП2'),
    ('3', 'ТЭ до 1г.'),
    ('4', 'ТЭ св 1г(1).'),
    ('5', 'ТЭ св 1г(2)'),
    ('6', 'ТЭ св 3-х лет'),
    ('7', 'ТЭ св 3-х лет(2)'),
    ('8', 'ТЭ св 3-х лет(3)'),
    ('9', 'ССМ(1)'),
    ('10', 'ССМ(2)'),
    ('11', 'ССМ(3)'),
    ('12', 'ВСМ')
    ]

class Group(models.Model):
    stage = models.CharField(max_length=255, choices=stage_choices)
    group_name = models.CharField(max_length=255)


# Далее переходим в admin.py импортируем все модели, далее регестрируем их
# Create your models here.
