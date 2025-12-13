from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from.models import CustomUser
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError 



class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'autofocus':True, 'placeholder':'Укажите Вашу эллектронную почту','class':'form-control'})
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль', 'class':'form-control password'}) 
    )

    def clean(self):# Кастомная функция для входа по email 
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(email=email, password = password)

        if user is None:
            raise ValidationError('Неверный email или пароль')

        self.user = user
        return self.cleaned_data

    def get_user(self):
        return self.user
   