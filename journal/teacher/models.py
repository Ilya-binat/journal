from django.db import models
from datetime import date
# Модель Д.З
class Homework(models.Model):
    DRAFT = 'draft'
    ACTIVE = 'active'
    CLOSED = 'closed'

    STATUS_CHOICES = [
        (DRAFT, 'Черновик'),
        (ACTIVE, 'Активно'),
        (CLOSED, 'Закрыто'),
    ]
    group = models.ForeignKey(
        'administrator.Group',
        on_delete=models.CASCADE,
        related_name='homeworks'
    )
    author = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='homeworks'
    )
    title = models.CharField(max_length=255)
    text = models.TextField()
    date = models.DateField(auto_now_add=True)
    deadline = models.DateField(null=True, blank=True)
    file = models.FileField(upload_to='homework/%Y/%m', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ACTIVE)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f'{self.group}:{self.title}'


