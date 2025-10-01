from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
import csv
import io

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
        fields = ['first_name', 'last_name', 'cpf', 'telefone', 'endereco', 'data_nascimento']
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'cpf': 'CPF',
            'telefone': 'Telefone',
            'endereco': 'Endereço',
            'data_nascimento': 'Data de Nascimento'
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 99999-9999'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Digite seu endereço completo'}),
            'data_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        help_texts = {
            'cpf': 'Digite apenas números ou use o formato 000.000.000-00',
            'endereco': 'Endereço completo incluindo rua, número, bairro, cidade e CEP',
        }


class UserManagementForm(forms.ModelForm):
    """Formulário para gestores criarem/editarem usuários"""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label='Senha',
        help_text='Deixe em branco para manter a senha atual (apenas na edição)'
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'user_type', 'cpf', 'telefone', 'endereco', 'data_nascimento'
        ]
        labels = {
            'username': 'Nome de usuário',
            'email': 'E-mail',
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'user_type': 'Tipo de usuário',
            'cpf': 'CPF',
            'telefone': 'Telefone',
            'endereco': 'Endereço',
            'data_nascimento': 'Data de Nascimento'
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 99999-9999'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'data_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)
        
        if self.is_edit:
            self.fields['password'].help_text = 'Deixe em branco para manter a senha atual'
            self.fields['password'].required = False
        else:
            self.fields['password'].required = True
            self.fields['password'].help_text = 'Digite uma senha para o usuário'

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Se uma nova senha foi fornecida
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
        return user


class CSVUploadForm(forms.Form):
    """Formulário para upload de CSV com usuários"""
    
    csv_file = forms.FileField(
        label='Arquivo CSV',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        }),
        help_text='Formato: username,email,first_name,last_name,user_type,cpf,telefone,password'
    )
    
    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            raise forms.ValidationError('O arquivo deve ter extensão .csv')
        
        # Verificar se o arquivo não está vazio
        if csv_file.size == 0:
            raise forms.ValidationError('O arquivo CSV está vazio')
        
        # Verificar se o arquivo não é muito grande (5MB)
        if csv_file.size > 5 * 1024 * 1024:
            raise forms.ValidationError('O arquivo é muito grande. Máximo 5MB.')
        
        return csv_file
    
    def process_csv(self):
        """Processa o arquivo CSV e retorna lista de usuários para criar"""
        csv_file = self.cleaned_data['csv_file']
        
        # Ler o arquivo CSV
        file_data = csv_file.read().decode('utf-8')
        csv_data = csv.DictReader(io.StringIO(file_data))
        
        users_to_create = []
        errors = []
        
        required_fields = ['username', 'email', 'password']
        
        for row_num, row in enumerate(csv_data, start=2):  # Start=2 porque linha 1 é header
            # Verificar campos obrigatórios
            missing_fields = [field for field in required_fields if not row.get(field, '').strip()]
            if missing_fields:
                errors.append(f'Linha {row_num}: Campos obrigatórios faltando: {", ".join(missing_fields)}')
                continue
            
            # Verificar se username já existe
            if CustomUser.objects.filter(username=row['username'].strip()).exists():
                errors.append(f'Linha {row_num}: Nome de usuário "{row["username"].strip()}" já existe')
                continue
            
            # Verificar se email já existe
            if CustomUser.objects.filter(email=row['email'].strip()).exists():
                errors.append(f'Linha {row_num}: E-mail "{row["email"].strip()}" já existe')
                continue
            
            # Preparar dados do usuário
            user_data = {
                'username': row['username'].strip(),
                'email': row['email'].strip(),
                'first_name': row.get('first_name', '').strip(),
                'last_name': row.get('last_name', '').strip(),
                'user_type': row.get('user_type', 'monitor').strip(),
                'cpf': row.get('cpf', '').strip(),
                'telefone': row.get('telefone', '').strip(),
                'password': row['password'].strip(),
            }
            
            # Validar user_type
            valid_types = ['admin', 'gestor', 'monitor']
            if user_data['user_type'] not in valid_types:
                user_data['user_type'] = 'monitor'
            
            users_to_create.append(user_data)
        
        return users_to_create, errors

