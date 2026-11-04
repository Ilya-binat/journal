import re

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import *
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError


class RegisterForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "placeholder": "Укажите имя",
                "class": "form-control",
            }
        )
    )

    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "placeholder": "Укажите фамилию",
                "class": "form-control",
            }
        )
    )

    middle_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "placeholder": "Укажите отчество",
                "class": "form-control",
            }
        )
    )

    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        required=True

    )

    email = forms.CharField(
        widget=forms.EmailInput(
            attrs={"placeholder": "Укажите эллектронную почту", "class": "form-control"}
        )
    )
    phone_number = forms.CharField(
        max_length=12,
        widget=forms.TextInput(
            attrs={"placeholder": "Укажите номер телефона", "class": "form-control"}
        ),
    )

    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = CustomUser
        fields = [
            "last_name",
            "first_name",
            "middle_name",
            "birth_date",
            "email",
            "phone_number",
            "role",
        ]


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "autofocus": True,
                "placeholder": "Укажите Вашу эллектронную почту",
                "class": "form-control",
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Введите пароль", "class": "form-control password"}
        )
    )

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        user = authenticate(username=email, password=password)

        if user is None:
            raise ValidationError("Неверный email или пароль")

        self.user = user
        return self.cleaned_data

    def get_user(self):
        return getattr(self, 'user', None)


AVATAR_MAX_SIZE = 1024 * 1024 * 2
AVATAR_FORMATS = ('JPEG', 'PNG', 'WEBP')


# Функция очистки номера телефона
def normalize_phone(raw):
    digits = re.sub(r"\D", '', raw or '')

    if not digits:
        return None
    if len(digits) == 10:
        digits = '7' + digits
    elif len(digits) == 11 and digits[0] in '78':  # in - проверяет вхождение. 78 это не цифра 78, а 7 или 8
        digits = '7' + digits[1:]
    else:
        raise ValidationError('Ввеите номер в формате: +7XXXXXXXXXX')
    return digits


class ProfileForm(forms.ModelForm):
    last_name = forms.CharField(
        label='Фамилия',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    first_name = forms.CharField(
        label='Имя',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    middle_name = forms.CharField(
        label='Отчество',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    birth_date = forms.DateField(
        label='Дата рождения',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }, format='%Y-%m-%d')
    )

    email = forms.EmailField(
        label='Почта',
        widget=forms.EmailInput(attrs={
            'class': 'form-control'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['last_name', 'first_name', 'middle_name', 'birth_date', 'email']

    # Проверяет уникальность email
    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()

        if CustomUser.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Этот email уже используется другим пользователем')
        return email

    # Сохраняет в качестве username поле почты
    def save(self, commit=True):
        user = super().save(commit=False)

        user.username = user.email

        if commit:
            user.save()
        return user


# Форма редактирования номера телефона
class PhoneForm(forms.Form):
    phone_number = forms.CharField(required=False)

    def clean_phone_number(self):
        return normalize_phone(self.cleaned_data.get('phone_number'))


# Форма аватарки пользователя
class AvatarForm(forms.Form):
    avatar = forms.ImageField(error_messages={
        'required': 'Выберите файл',
        'invalid_image': 'Файл не является изображением',
        'invalid': 'Файл не является изображением'
    })

    # Функция проверки аватрки на нужный формат и нужный размер
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')

        if avatar.size > AVATAR_MAX_SIZE:
            raise ValidationError('Файл слишком большой: Максимум 2 MB')
        if getattr(avatar.image, 'format', None) not in AVATAR_FORMATS:
            raise ValidationError('Допустимые форматы: JPEG, PNG, WEBP')
        return avatar


# Форма редактирования пароля
class StyledPasswordChangeForm(PasswordChangeForm):
    error_messages = {
        **PasswordChangeForm.error_messages,
        'password_incorrect': 'Текущий пароль введен не верно',
        'password_mismatch': 'Пароли не совпадают',
    }

    # Функция init для изменения лейблов и виджетов полей
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        labels = {
            'old_password': 'Текущий пароль',
            'new_password1': 'Новый пароль',
            'new_password2': 'Повторите новый пароль'
        }
        for name, field in self.fields.items():
            field.label = labels[name]
            field.widget.attrs.update({'class': 'form-control'})
