from django.db import models
from core.models import CustomUser

TIPO_TEMPORADA = (
    ('ferias', 'Férias'),
    ('familia', 'Familia'),
    ('dayuse', 'Day Use'),
    ('evento', 'Evento Especial'),
)

class Temporada(models.Model):
    nome = models.CharField(max_length=100)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    cliente = models.CharField(max_length=100, blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_TEMPORADA)
    email_enviado = models.BooleanField(default=False)

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
