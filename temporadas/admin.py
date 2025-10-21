from django.contrib import admin
from .models import Temporada, ConfiguracaoValores, AjudaCustoClasse, TemporadaEquipe


class TemporadaEquipeInline(admin.TabularInline):
    model = TemporadaEquipe
    extra = 0


@admin.register(Temporada)
class TemporadaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'data_inicio', 'data_fim', 'tipo', 'numero_diarias', 'email_enviado')
    list_filter = ('tipo', 'email_enviado')
    inlines = [TemporadaEquipeInline]


admin.site.register(ConfiguracaoValores)
admin.site.register(AjudaCustoClasse)
