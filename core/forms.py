from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    cpf = forms.CharField(
        max_length=14, 
        required=True,
        label='CPF',
        widget=forms.TextInput(attrs={
            'placeholder': '000.000.000-00',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'cpf', 'password1', 'password2']
        labels = {
            'username': 'Nome de usuário',
            'email': 'E-mail',
            'password1': 'Senha',
            'password2': 'Confirme a senha'
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'monitor'  # Define automaticamente como monitor
        user.cpf = self.cleaned_data['cpf']
        if commit:
            user.save()
        return user


class CompleteProfileForm(forms.ModelForm):
    """Formulário para completar o perfil do monitor"""
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'telefone', 'endereco', 'data_nascimento']
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'telefone': 'Telefone',
            'endereco': 'Endereço',
            'data_nascimento': 'Data de Nascimento'
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 99999-9999'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'data_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
