from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from.models import CustomUser
from django.contrib.auth import authenticate

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


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'autofocus':True, 'placeholder':'Укажите Вашу эллектронную почту'})
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль', 'class':'password'}) 
    )

    def clean(self):# Кастомная функция для входа по email 
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(email=email, password = password)
        self.user = user
        return self.cleaned_data

    def get_user(self):
        return self.user
    
    class Meta:
        model = CustomUser
        fields = ['username', 'password']