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


# Модель расписания 
class Schedule(models.Model):
    coach = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        limit_choices_to={'role':'Тренер'}
    )

    group = models.ForeignKey('administrator.Group', on_delete=models.CASCADE)
    hall = models.ForeignKey('administrator.Hall', on_delete=models.CASCADE)

    weekday = models.IntegerField(choices=[
        (1,'Понедельник'),
        (2,'Вторник'),
        (3,'Среда'),
        (4,'Четверг'),
        (5,'Пятница'),
        (6,'Суббота'),
        (7,'Воскресенье'),
    ])
    #  Связь с расписания с периодами
    period = models.ForeignKey(
        'administrator.SchedulePeriod',
        on_delete=models.CASCADE,
        related_name="schedules"
    )  

    start_time = models.TimeField()
    end_time = models.TimeField()

    is_active = models.BooleanField(default=True)

# Модель периода 
class SchedulePeriod(models.Model):
    name = models.CharField(max_length=100)  # Имя периода  
    date_start = models.DateField()
    date_end = models.DateField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.date_start} – {self.date_end})"
    
