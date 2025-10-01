from django.db import models
from core.models import CustomUser

TIPO_TEMPORADA = (
    ('escola', 'Escola'),  # Adicionado conforme documento
    ('dayuse', 'Day Use'),
    ('familia', 'Família'),
    ('ferias', 'Férias'),
    ('evento', 'Evento Especial'),
)

class Temporada(models.Model):
    # Campos básicos
    data_inicio = models.DateField(verbose_name='Data de Início')
    data_fim = models.DateField(verbose_name='Data de Fim')
    cliente = models.CharField(max_length=100, blank=True, null=True, verbose_name='Cliente')
    tipo = models.CharField(max_length=20, choices=TIPO_TEMPORADA, verbose_name='Tipo')
    
    # Novos campos de horário
    horario_chegada_equipe = models.TimeField(verbose_name='Horário Chegada Equipe', blank=True, null=True)
    horario_saida_equipe = models.TimeField(verbose_name='Horário Saída Equipe', blank=True, null=True)
    
    # Campo de diárias (permite fracionado)
    numero_diarias = models.DecimalField(
        max_digits=4, 
        decimal_places=1, 
        default=1.0,
        verbose_name='Número de Diárias',
        help_text='Ex: 3.5 para três dias e meio'
    )
    
    # Campos de remuneração adicional
    tem_embarque = models.BooleanField(default=False, verbose_name='Tem Embarque')
    tem_desembarque = models.BooleanField(default=False, verbose_name='Tem Desembarque')
    tem_ajuda_custo = models.BooleanField(default=False, verbose_name='Tem Ajuda de Custo')
    
    # Campo de controle de email
    email_enviado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.cliente or 'Cliente não informado'} ({self.data_inicio} - {self.data_fim})"

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
        return f"{self.monitor.username} - {self.temporada} ({self.status})"
