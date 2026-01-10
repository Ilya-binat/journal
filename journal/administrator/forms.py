from django import forms
from users.models import CustomUser
from .models import stage_choices, Group


# Для создания группы
class GroupForm(forms.ModelForm):
    group_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "placeholder": "Название группы",
                "class": "form-control",
            }
        )
    )

    stage = forms.ChoiceField(
        choices=stage_choices, widget=forms.Select(attrs={"class": "form-select"})
    )

    coach = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role = 'Тренер'), 
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = Group
        fields = [
            'group_name',
            'stage',
            'coach'
        ]

