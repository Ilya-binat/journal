from django import forms
from users.models import CustomUser
from .models import stage_choices, Group, SchedulePeriod


# Для создания группы
class GroupForm(forms.ModelForm):
    group_name = forms.CharField(
        label='Название группы',
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "placeholder": "Название группы",
                "class": "form-control",
            }
        )
    )

    stage = forms.ChoiceField(
        label='Этап подготовки',
        choices=stage_choices, widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = Group
        fields = [
            'group_name',
            'stage',
            
        ]

# Форма для добавления периода

class PeriodForm(forms.ModelForm):
    name =  forms.CharField(
        label='Название периода',
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "placeholder": "Название периода",
                "class": "form-control",
            }
        )
    )
    date_start = forms.DateField(
        label="Дата начала",
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control"
            }
        )
    )

    date_end = forms.DateField(
        label="Дата окончания",
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control"
            }
        )
    )

    class Meta:
        model = SchedulePeriod
        fields = ["name", "date_start", "date_end"]