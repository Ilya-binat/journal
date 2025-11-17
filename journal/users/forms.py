from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from.models import CustomUser
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError 

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Укажите Ваше имя','class':'form-control'})
    )

    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Укажите Вашу фамилию','class':'form-control'})
    )

    middle_name = forms.CharField(
        widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Укажите Ваше отчество','class':'form-control'})
    )
    
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'placeholder':'Укажите Вашу эллектронную почту','class':'form-control'})
    )
    phone_number = forms.CharField(max_length=12,
        widget=forms.TextInput(attrs={'placeholder': 'Укажите Ваш номер телефона','class':'form-control'})
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль','class':'form-control'})
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль','class':'form-control'})
    )

    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
)

    class Meta:
        model = CustomUser
        fields = ['last_name', 'first_name', 'middle_name', 'email', 'phone_number', 'password1', 'password2', 'role']


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
   