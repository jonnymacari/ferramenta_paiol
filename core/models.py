from django.contrib.auth.models import AbstractUser
from django.db import models
from .monitor_categories import CATEGORIAS_MONITOR, CATEGORIAS_AJUDA_CUSTO

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
    
    # Status de aprovação para monitores
    is_approved = models.BooleanField(default=False, verbose_name='Aprovado')
    
    # Categorias do monitor (definidas pelo gestor)
    categoria_funcao = models.CharField(
        max_length=30, 
        choices=CATEGORIAS_MONITOR, 
        blank=True, 
        null=True,
        verbose_name='Categoria da Função'
    )
    categoria_ajuda_custo = models.CharField(
        max_length=20, 
        choices=CATEGORIAS_AJUDA_CUSTO, 
        blank=True, 
        null=True,
        verbose_name='Categoria Ajuda de Custo'
    )
    
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
                self.data_nascimento and
                self.cpf  # CPF também é necessário para completude
            )
            
            # Monitores criados por gestores/admins são aprovados automaticamente
            # Monitores que se auto-cadastram precisam de aprovação manual
            if not self.pk:  # Novo usuário
                # Se não foi definido explicitamente, assumir que precisa aprovação
                if not hasattr(self, '_created_by_manager'):
                    self.is_approved = False
        else:
            # Para outros tipos de usuário, considerar sempre completo e aprovado
            self.cadastro_completo = True
            self.is_approved = True
        
        super().save(*args, **kwargs)
    
    def get_valor_diaria(self):
        """Retorna o valor da diária baseado na categoria"""
        if self.categoria_funcao:
            from .monitor_categories import get_valor_diaria
            return get_valor_diaria(self.categoria_funcao)
        return 0.00
    
    def get_valor_ajuda_custo(self):
        """Retorna o valor da ajuda de custo baseado na categoria"""
        if self.categoria_ajuda_custo:
            from .monitor_categories import get_valor_ajuda_custo
            return get_valor_ajuda_custo(self.categoria_ajuda_custo)
        return 0.00
