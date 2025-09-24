from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Nome de usuário',
            'email': 'E-mail',
            'password1': 'Senha',
            'password2': 'Confirme a senha'
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'monitor'  # Define automaticamente como monitor
        if commit:
            user.save()
        return user
