from django import forms
from administrator.models import Group
from .models import Homework
from datetime import date


class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ['group', 'title', 'text', 'deadline', 'file']
        labels = {
            'group': 'Группа',
            'title': 'Тема',
            'text': 'Задание',
            'deadline': 'Срок выполнения',
            'file': 'Файл',
        }
        widgets = {
            'group': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, coach=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].queryset = Group.objects.filter(coach=coach)

    def clean(self):
        cleaned = super().clean()
        deadline = cleaned.get('deadline')
        start = self.instance.date if self.instance.pk else date.today()
        if deadline and deadline < start:
            self.add_error('deadline', 'Срок выполнения не может быть раньше даты выдачи')
        return cleaned
