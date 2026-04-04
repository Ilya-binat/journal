from django.db import models


class Coach(models.Model):
    first_name = models.CharField(max_length=255)
    last_name  = models.CharField(max_length=255)
    middle_name  = models.CharField(max_length=255)

# Модель вида спорта
class TrainingType(models.Model):
    name = models.CharField(max_length=255)

# str функция отображает поле name вместо TrainingType object
    def __str__(self):
        return self.name

class Hall(models.Model):
    hall_name = models.CharField(max_length=255)
    training_type = models.ForeignKey('administrator.TrainingType', on_delete=models.SET_NULL, null=True, blank=True)#on_delet=models.SET_NULL - при удаление вида спорта не будет удален зал, а тип спорта станет нулевым.

# Модель тренировки
class Slot(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    coach = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True, blank=True) # null - делает поле не обязательным в базе данных
    hall = models.ForeignKey('administrator.Hall', on_delete=models.SET_NULL, null=True, blank=True) # blank - делает поле не обязательным в форме
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

    def __str__(self):
        return self.group_name

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

    weekdays = models.ManyToManyField('administrator.WeekDay')
    #  Связь с расписания с периодами
    period = models.ForeignKey(
        'administrator.SchedulePeriod',
        on_delete=models.CASCADE,
        related_name="schedules"
    )  

    start_time = models.TimeField()
    end_time = models.TimeField()

    is_active = models.BooleanField(default=True)


# __str__ функция - 
    def __str__(self):
        return f'{self.coach.get_short_name()} - {self.group.group_name}' 
    
   
# Модель периода 
class SchedulePeriod(models.Model):
    name = models.CharField(max_length=100)  # Имя периода  
    date_start = models.DateField()
    date_end = models.DateField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.date_start} – {self.date_end})"
    
# Модель дня недели 

class WeekDay(models.Model):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=2, null=True)



    def __str__(self):
        return self.name
    
STATUS_CHOICES=[
    ('present','Присутствовал'),
    ('absent','Отсутствовал'),
    ('excused', 'Уважительная причина'),
    ('late', 'Опаздал')
]

# Модель расписания
class Attendance(models.Model):
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='attendances', limit_choices_to={'role':'Спортсмен'})
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='absent')
    note = models.CharField(max_length=255, blank = True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('slot','student')

    def __str__(self):
        return f'{self.student} — {self.slot.date} ({self.get_status_display()})'
    
# Модель графика соревнований

class Competition(models.Model):
    title = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    sport_type = models.ForeignKey(TrainingType, on_delete=models.CASCADE)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()

    class Meta:
        unique_together = ('title','sport_type', 'date_start', 'date_end')

    def __str__(self):
        return f'{self.title} - {self.date_start} -{self.date_end}'
    

# Модель КПИ

class Assessment(models.Model):
    name = models.CharField(max_length=255)
    coach = models.ForeignKey('users.CustomUser', 
            on_delete=models.CASCADE, 
            limit_choices_to={'role':'Тренер'})
    group = models.ForeignKey(
         'administrator.Group',
        on_delete=models.CASCADE,
    )
    sport_type = models.ForeignKey(TrainingType, on_delete=models.CASCADE)
    next_stage = models.CharField(choices=stage_choices, max_length=255)
    is_passed = models.BooleanField(default=False)
    date_start = models.DateField()
    date_end = models.DateField()

    
    class Meta:
        unique_together = ('name','coach', 'group', 'date_start', 'date_end')

    def __str__(self):
        return f'{self.name} - {self.group}-{self.date_start} -{self.date_end}'

