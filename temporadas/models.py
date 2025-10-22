from django.db import models
from core.models import CustomUser

# Tipos de temporada (Escola no topo)
TIPO_TEMPORADA = (
    ('escola', 'Escola'),
    ('dayuse', 'Day Use'),
    ('familia', 'Família'),
    ('ferias', 'Férias'),
    ('evento', 'Evento Especial'),
)


class ConfiguracaoValores(models.Model):
    """Valores de diária por função, incluindo Day Camp (Day Use)."""
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    conselheiro_senior = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    conselheiro = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    monitor = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    monitor_junior = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    estagiario = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    day_camp = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text='Valor usado para tipo Day Use')
    enfermeira = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    enfermeira_estagiaria = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    fotografo_1 = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    fotografo_2 = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Configuração de Valores'
        verbose_name_plural = 'Configurações de Valores'

    def __str__(self):
        return f"Configuração #{self.id} - {self.atualizado_em:%d/%m/%Y}"


class AjudaCustoClasse(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    valor = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = 'Classe de Ajuda de Custo'
        verbose_name_plural = 'Classes de Ajuda de Custo'

    def __str__(self):
        return f"{self.nome} - R$ {self.valor}"


class Temporada(models.Model):
    nome = models.CharField(max_length=100)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    cliente = models.CharField(max_length=100, blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_TEMPORADA)
    email_enviado = models.BooleanField(default=False)

    # Novos campos
    hora_chegada_equipe = models.TimeField(blank=True, null=True)
    hora_saida_equipe = models.TimeField(blank=True, null=True)
    numero_diarias = models.DecimalField(max_digits=4, decimal_places=1, default=1)

    # Equipe (monitores) da temporada
    monitores = models.ManyToManyField(CustomUser, through='TemporadaEquipe', related_name='temporadas')

    def __str__(self):
        return f"{self.nome} ({self.data_inicio} - {self.data_fim})"


STATUS_INTERESSE = (
    ('interessado', 'Interessado'),
    ('aprovado', 'Aprovado'),
    ('recusado', 'Recusado'),
    ('confirmado', 'Confirmado'),
)


class InteresseTemporada(models.Model):
    monitor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'monitor'})
    temporada = models.ForeignKey(Temporada, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_INTERESSE, default='interessado')
    data_interesse = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('monitor', 'temporada')

    def __str__(self):
        return f"{self.monitor.username} - {self.temporada.nome} ({self.status})"


STATUS_EQUIPE = (
    ('pendente', 'Pendente'),
    ('confirmado', 'Confirmado'),
    ('concluido', 'Concluído'),
)


class TemporadaEquipe(models.Model):
    temporada = models.ForeignKey(Temporada, on_delete=models.CASCADE)
    monitor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'monitor'})
    status = models.CharField(max_length=20, choices=STATUS_EQUIPE, default='pendente')

    recebe_ajuda_custo = models.BooleanField(default=False)
    ajuda_custo_classe = models.ForeignKey(AjudaCustoClasse, on_delete=models.SET_NULL, blank=True, null=True)

    recebe_embarque = models.BooleanField(default=False)
    valor_embarque_especial = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    recebe_desembarque = models.BooleanField(default=False)
    valor_desembarque_especial = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    class Meta:
        unique_together = ('temporada', 'monitor')

    def __str__(self):
        return f"{self.monitor.username} em {self.temporada.nome} ({self.get_status_display()})"

