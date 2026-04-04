from django import forms
from users.models import CustomUser
from .models import *


# Для создания группы
class GroupForm(forms.ModelForm):
    group_name = forms.CharField(
        label="Название группы",
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "placeholder": "Название группы",
                "class": "form-control",
            }
        ),
    )

    stage = forms.ChoiceField(
        label="Этап подготовки",
        choices=stage_choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Group
        fields = [
            "group_name",
            "stage",
        ]


# Форма для добавления периода


class PeriodForm(forms.ModelForm):
    name = forms.CharField(
        label="Название периода",
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "placeholder": "Название периода",
                "class": "form-control",
            }
        ),
    )
    date_start = forms.DateField(
        label="Дата начала",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    date_end = forms.DateField(
        label="Дата окончания",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    class Meta:
        model = SchedulePeriod
        fields = ["name", "date_start", "date_end"]


class HallForm(forms.ModelForm):

    hall_name = forms.CharField(
        label="Номер зала",
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "placeholder": "Номер зала",
                "class": "form-control",
            }
        ),
    )

    training_type = forms.ModelChoiceField(
        queryset=TrainingType.objects.all(),
        required=False,
        label="Тип тренировки",
        empty_label="Выберите тип тренировки",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    class Meta:
        model = Hall
        fields = ["hall_name", "training_type"]


#  Форма добавления расписания


class ScheduleForm(forms.Form):

    coach = forms.IntegerField()
    group = forms.IntegerField()
    hall = forms.IntegerField()
    period = forms.IntegerField()
    weekdays = forms.MultipleChoiceField(choices=[])
    start_time = forms.TimeField()
    end_time = forms.TimeField()

    # Функция загрузки дней недели из базы данных

    def __init__(self, *args, exclude_pk=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.exclude_pk = exclude_pk

        self.fields["weekdays"].choices = [
            (wd.id, wd.name) for wd in WeekDay.objects.all()
        ]

    # Функция проверки уникальности расписания

    def clean(self):
        cleaned_data = super().clean()
        coach_id = cleaned_data.get("coach")
        weekdays = cleaned_data.get("weekdays")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        #  Проверка пересечения тренировоак по времени и дням недели
        if coach_id and weekdays and start_time and end_time:
            for weekday in weekdays:
                conflict = (
                    Schedule.objects.filter(coach_id=coach_id, weekdays__id=weekday)
                    .filter(start_time__lt=end_time, end_time__gt=start_time)
                    .exclude(pk=self.exclude_pk)
                )
                if conflict:
                    raise forms.ValidationError(
                        "У тренера уже есть занятие в этот день недели, в указанное время"
                    )

        return cleaned_data


class CompetitionForm(forms.ModelForm):
    title = forms.CharField(
        label="Название соревнования",
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "placeholder": "Название соревнования",
                "class": "form-control",
            }
        ),
    )

    sport_type = forms.ModelChoiceField(
        queryset=TrainingType.objects.all(),
        required=False,
        label="Вид спорта",
        empty_label="Выберите вид спорта",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    address = forms.CharField(
        label="Место проведения",
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "placeholder": "Место проведения",
                "class": "form-control",
            }
        ),
    )

    date_start = forms.DateTimeField(
        label="Дата начала",
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"}
        ),
    )

    date_end = forms.DateTimeField(
        label="Дата окончания",
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"}
        ),
    )

    class Meta:
        model = Competition
        fields = ["title", "sport_type", "address", "date_start", "date_end"]


# Форма КПИ


class AssessmentForm(forms.ModelForm):
    name = forms.CharField(
        label="Название КПИ",
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "placeholder": "Название КПИ",
                "class": "form-control",
            }
        ),
    )
    coach = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role="Тренер"),
        required=True,
        label="Тренер",
        empty_label="Выберите тренера",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        label="Группа",
        empty_label="Выберите группу",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    sport_type = forms.ModelChoiceField(
        queryset=TrainingType.objects.all(),
        required=False,
        label="Вид спорта",
        empty_label="Выберите вид спорта",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    next_stage = forms.ChoiceField(
        label="Перевод на следующий этап",
        choices=stage_choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    date_start = forms.DateField(
        label="Дата начала",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    date_end = forms.DateField(
        label="Дата окончания",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    class Meta:
        model = Assessment
        fields = [
            "name",
            "coach",
            "group",
            "sport_type",
            "next_stage",
            "date_start",
            "date_end",
        ]
