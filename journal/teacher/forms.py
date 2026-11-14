from django import forms
from administrator.models import Group
from .models import Homework


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
        start, end = cleaned.get('date'), cleaned.get('deadline')
        if start and end and start > end:
            self.add_error('deadline', 'Срок сдачи не может быть раньше даты выдочи')
        return cleaned
