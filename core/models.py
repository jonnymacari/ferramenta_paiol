from django.contrib.auth.models import AbstractUser
from django.db import models

USER_TYPES = (
    ('admin', 'Admin'),
    ('gestor', 'Gestor'),
    ('monitor', 'Monitor'),
)

class CustomUser(AbstractUser):
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='monitor')
    cpf = models.CharField(max_length=14, blank=True, null=True, verbose_name='CPF')
    
    # Campos que podem ficar pendentes para monitores
    first_name = models.CharField(max_length=150, blank=True, verbose_name='Nome')
    last_name = models.CharField(max_length=150, blank=True, verbose_name='Sobrenome')
    telefone = models.CharField(max_length=15, blank=True, null=True, verbose_name='Telefone')
    endereco = models.TextField(blank=True, null=True, verbose_name='Endereço')
    data_nascimento = models.DateField(blank=True, null=True, verbose_name='Data de Nascimento')
    
    # Status do cadastro para monitores
    cadastro_completo = models.BooleanField(default=False, verbose_name='Cadastro Completo')
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    def save(self, *args, **kwargs):
        # Para monitores, verificar se o cadastro está completo
        if self.user_type == 'monitor':
            self.cadastro_completo = bool(
                self.first_name and 
                self.last_name and 
                self.telefone and 
                self.endereco and 
                self.data_nascimento
            )
        else:
            # Para outros tipos de usuário, considerar sempre completo
            self.cadastro_completo = True
        
        super().save(*args, **kwargs)
