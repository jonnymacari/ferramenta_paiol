from django import forms
from decimal import Decimal, InvalidOperation
from .models import Temporada, ConfiguracaoValores, AjudaCustoClasse


class TemporadaForm(forms.ModelForm):
    """Formulário de Temporada: oculta 'nome' e aplica regras de negócio."""

    class Meta:
        model = Temporada
        fields = [
            # 'nome' oculto (preenchido automaticamente)
            'data_inicio', 'data_fim', 'cliente', 'tipo',
            'hora_chegada_equipe', 'hora_saida_equipe', 'numero_diarias'
        ]
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cliente': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'hora_chegada_equipe': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_saida_equipe': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'numero_diarias': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: 1, 1.5, 2, 2,5'}),
        }

    def clean_numero_diarias(self):
        valor = self.data.get('numero_diarias') or self.cleaned_data.get('numero_diarias')
        if isinstance(valor, (int, float, Decimal)):
            dec = Decimal(str(valor))
        else:
            texto = str(valor).strip().replace(',', '.')
            try:
                dec = Decimal(texto)
            except (InvalidOperation, TypeError):
                raise forms.ValidationError('Número de diárias inválido. Use números como 1, 1.5 ou 2,5.')

        # Arredonda para 0.5
        metade = (dec * 2)
        if metade != metade.to_integral_value():
            raise forms.ValidationError('Número de diárias deve ser múltiplo de 0,5.')

        return dec

    def clean(self):
        cleaned = super().clean()

        tipo = cleaned.get('tipo')
        diarias = cleaned.get('numero_diarias')
        data_inicio = cleaned.get('data_inicio')
        data_fim = cleaned.get('data_fim')

        # Regra Day Use: força 1 diária
        if tipo == 'dayuse':
            cleaned['numero_diarias'] = Decimal('1.0')

        # Preenche 'nome' automaticamente se vazio
        if not getattr(self.instance, 'nome', None):
            if data_inicio and data_fim and tipo:
                tipo_label = dict(self.fields['tipo'].choices).get(tipo, tipo)
                self.instance.nome = f"{tipo_label} {data_inicio:%d/%m} - {data_fim:%d/%m/%Y}"

        return cleaned


class ConfiguracaoValoresForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoValores
        fields = [
            'conselheiro_senior', 'conselheiro', 'monitor', 'monitor_junior', 'estagiario',
            'day_camp', 'enfermeira', 'enfermeira_estagiaria', 'fotografo_1', 'fotografo_2'
        ]


class AjudaCustoClasseForm(forms.ModelForm):
    class Meta:
        model = AjudaCustoClasse
        fields = ['nome', 'valor']
