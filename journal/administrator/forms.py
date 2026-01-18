from django import forms
from users.models import CustomUser
from .models import stage_choices, Group


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

