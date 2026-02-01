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
    coach = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    hall = models.ForeignKey('administrator.Hall', on_delete=models.SET_NULL, null=True, blank=True)
    group = models.ForeignKey('administrator.Group', on_delete=models.SET_NULL, null=True, blank=True)

stage_choices = [
    ('НП1', 'НП1'),
    ('НП2', 'НП2'),
    ('ТЭ до 1г.', 'ТЭ до 1г.'),
    ('ТЭ св 1г(1).', 'ТЭ св 1г(1).'),
    ('ТЭ св 1г(2)', 'ТЭ св 1г(2)'),
    ('ТЭ св 3-х лет', 'ТЭ св 3-х лет'),
    ('ТЭ св 3-х лет(2)', 'ТЭ св 3-х лет(2)'),
    ('ТЭ св 3-х лет(3)', 'ТЭ св 3-х лет(3)'),
    ('ССМ(1)', 'ССМ(1)'),
    ('ССМ(2)', 'ССМ(2)'),
    ('ССМ(3)', 'ССМ(3)'),
    ('ВСМ', 'ВСМ')
    ]

class Group(models.Model):
    stage = models.CharField(max_length=255, choices=stage_choices)
    group_name = models.CharField(max_length=255, unique=True)
    coach = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, 
    related_name='coach_groups')

class StudentGroup(models.Model):
    student = models.OneToOneField(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='current_groups',
        limit_choices_to={'role':'Спортсмен'},
    )
    group = models.ForeignKey(
        'administrator.Group',
        on_delete=models.CASCADE,
        related_name='group_students',
    )
# Далее переходим в admin.py импортируем все модели, далее регестрируем их
# Create your models here.
