from django.contrib.auth.models import AbstractUser
from django.db import models

USER_TYPES = (
    ('admin', 'Admin'),
    ('gestor', 'Gestor'),
    ('monitor', 'Monitor'),
)

ESTADO_CIVIL_CHOICES = (
    ('solteiro', 'Solteiro(a)'),
    ('casado', 'Casado(a)'),
    ('divorciado', 'Divorciado(a)'),
    ('viuvo', 'Viúvo(a)'),
    ('uniao_estavel', 'União Estável'),
)

class Endereco(models.Model):
    """Modelo para endereço completo"""
    cep = models.CharField(max_length=9, verbose_name='CEP')
    logradouro = models.CharField(max_length=255, verbose_name='Logradouro')
    numero = models.CharField(max_length=10, verbose_name='Número')
    complemento = models.CharField(max_length=100, blank=True, null=True, verbose_name='Complemento')
    bairro = models.CharField(max_length=100, verbose_name='Bairro')
    cidade = models.CharField(max_length=100, verbose_name='Cidade')
    estado = models.CharField(max_length=2, verbose_name='Estado')
    
    def __str__(self):
        return f"{self.logradouro}, {self.numero} - {self.bairro}, {self.cidade}/{self.estado}"

class CustomUser(AbstractUser):
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='monitor')
    
    # CPF será preenchido posteriormente no perfil
    cpf = models.CharField(max_length=11, unique=True, blank=True, null=True, verbose_name='CPF')
    
    # Campos que podem ficar pendentes para monitores (informações básicas)
    first_name = models.CharField(max_length=150, blank=True, verbose_name='Nome')
    last_name = models.CharField(max_length=150, blank=True, verbose_name='Sobrenome')
    telefone = models.CharField(max_length=15, blank=True, null=True, verbose_name='Telefone')
    endereco_simples = models.TextField(blank=True, null=True, verbose_name='Endereço Simples')
    data_nascimento = models.DateField(blank=True, null=True, verbose_name='Data de Nascimento')
    
    # Campos detalhados para monitores (informações pendentes)
    rg = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name='RG')
    data_emissao_rg = models.DateField(blank=True, null=True, verbose_name='Data de Emissão do RG')
    pis = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name='PIS')
    nome_completo = models.CharField(max_length=100, blank=True, null=True, verbose_name='Nome Completo')
    nome_mae = models.CharField(max_length=100, blank=True, null=True, verbose_name='Nome da Mãe')
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES, blank=True, null=True, verbose_name='Estado Civil')
    celular = models.CharField(max_length=15, blank=True, null=True, verbose_name='Celular')
    telefone_fixo = models.CharField(max_length=15, blank=True, null=True, verbose_name='Telefone Fixo')
    email_alternativo = models.EmailField(blank=True, null=True, verbose_name='E-mail Alternativo')
    
    # Informações profissionais e acadêmicas
    formacao_academica = models.CharField(max_length=100, blank=True, null=True, verbose_name='Formação Acadêmica')
    trabalha_atualmente = models.BooleanField(default=False, verbose_name='Trabalha Atualmente')
    ja_trabalhou_como_monitor = models.BooleanField(default=False, verbose_name='Já Trabalhou como Monitor')
    ja_foi_paioleiro = models.BooleanField(default=False, verbose_name='Já Foi Paioleiro')
    ja_frequentou_acampamento = models.BooleanField(default=False, verbose_name='Já Frequentou Acampamento')
    
    # Habilidades e características
    descricao_lider = models.TextField(blank=True, null=True, verbose_name='Descrição de Liderança')
    habilidade_manual = models.TextField(blank=True, null=True, verbose_name='Habilidade Manual')
    habilidade_artistica = models.TextField(blank=True, null=True, verbose_name='Habilidade Artística')
    pratica_esporte = models.TextField(blank=True, null=True, verbose_name='Pratica Esporte')
    instrumento = models.TextField(blank=True, null=True, verbose_name='Instrumento Musical')
    habilidade_extra = models.TextField(blank=True, null=True, verbose_name='Habilidade Extra')
    
    # Restrições alimentares
    restricao_alimentar = models.BooleanField(default=False, verbose_name='Possui Restrição Alimentar')
    qual_restricao = models.TextField(blank=True, null=True, verbose_name='Qual Restrição')
    
    # Redes sociais
    facebook = models.CharField(max_length=255, blank=True, null=True, verbose_name='Facebook')
    instagram = models.CharField(max_length=255, blank=True, null=True, verbose_name='Instagram')
    site = models.URLField(blank=True, null=True, verbose_name='Site Pessoal')
    
    # Endereço completo (relacionamento)
    endereco_completo = models.OneToOneField(Endereco, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Endereço Completo')
    
    # Status do cadastro para monitores
    cadastro_completo = models.BooleanField(default=False, verbose_name='Cadastro Completo')
    is_approved = models.BooleanField(default=False, verbose_name='Aprovado pelo Gestor')
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    @property
    def nome_display(self):
        """Retorna o nome completo ou nome de usuário"""
        if self.nome_completo:
            return self.nome_completo
        elif self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.username
    
    @property
    def informacoes_pendentes(self):
        """Retorna lista de informações que ainda precisam ser preenchidas"""
        if self.user_type != 'monitor':
            return []
        
        pendentes = []
        
        # Campos obrigatórios básicos
        if not self.first_name:
            pendentes.append('Nome')
        if not self.last_name:
            pendentes.append('Sobrenome')
        if not self.telefone:
            pendentes.append('Telefone')
        if not self.data_nascimento:
            pendentes.append('Data de Nascimento')
        
        # Campos detalhados
        if not self.rg:
            pendentes.append('RG')
        if not self.nome_completo:
            pendentes.append('Nome Completo')
        if not self.celular:
            pendentes.append('Celular')
        if not self.formacao_academica:
            pendentes.append('Formação Acadêmica')
        if not self.descricao_lider:
            pendentes.append('Descrição de Liderança')
        if not self.habilidade_manual:
            pendentes.append('Habilidade Manual')
        if not self.habilidade_artistica:
            pendentes.append('Habilidade Artística')
        if not self.pratica_esporte:
            pendentes.append('Pratica Esporte')
        if not self.instrumento:
            pendentes.append('Instrumento Musical')
        if not self.habilidade_extra:
            pendentes.append('Habilidade Extra')
        if not self.endereco_completo:
            pendentes.append('Endereço Completo')
        
        return pendentes
    
    @property
    def percentual_cadastro(self):
        """Retorna o percentual de completude do cadastro"""
        if self.user_type != 'monitor':
            return 100
        
        total_campos = 20  # Total de campos importantes
        pendentes = len(self.informacoes_pendentes)
        preenchidos = total_campos - pendentes
        
        return int((preenchidos / total_campos) * 100)
    
    def save(self, *args, **kwargs):
        # Para monitores, verificar se o cadastro está completo
        if self.user_type == 'monitor':
            # Cadastro básico completo
            cadastro_basico = bool(
                self.first_name and 
                self.last_name and 
                self.telefone and 
                self.data_nascimento
            )
            
            # Cadastro detalhado completo
            cadastro_detalhado = bool(
                self.rg and
                self.nome_completo and
                self.celular and
                self.formacao_academica and
                self.descricao_lider and
                self.habilidade_manual and
                self.habilidade_artistica and
                self.pratica_esporte and
                self.instrumento and
                self.habilidade_extra and
                self.endereco_completo
            )
            
            self.cadastro_completo = cadastro_basico and cadastro_detalhado
        else:
            # Para outros tipos de usuário, considerar sempre completo
            self.cadastro_completo = True
        
        super().save(*args, **kwargs)
