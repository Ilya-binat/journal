from django import forms
from django.contrib.auth.forms import UserCreationForm
from.models import CustomUser


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Укажите Ваше имя'})
    )

    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Укажите Вашу фамилию'})
    )

    middle_name = forms.CharField(
        widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Укажите Ваше отчество'})
    )
    
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'placeholder':'Укажите Вашу эллектронную почту'})
    )
    phone_number = forms.CharField(max_length=12,
        widget=forms.TextInput(attrs={'placeholder': 'Укажите Ваш номер телефона'})
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'})
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'})
    )

    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES
    )

    class Meta:
        model = CustomUser
        fields = ['last_name', 'first_name', 'middle_name', 'email', 'phone_number', 'password1', 'password2', 'role']
