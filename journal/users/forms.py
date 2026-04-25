from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
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