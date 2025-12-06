from django import forms
from users .models import CustomUser



class RegisterForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Укажите имя','class':'form-control'})
    )

    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Укажите фамилию','class':'form-control'})
    )

    middle_name = forms.CharField(
        widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Укажите отчество','class':'form-control'})
    )
    
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'placeholder':'Укажите эллектронную почту','class':'form-control'})
    )
    phone_number = forms.CharField(max_length=12,
        widget=forms.TextInput(attrs={'placeholder': 'Укажите номер телефона','class':'form-control'})
    )


    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
)

    class Meta:
        model = CustomUser
        fields = ['last_name', 'first_name', 'middle_name', 'email', 'phone_number', 'role']