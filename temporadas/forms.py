from django import forms
from .models import Temporada

class TemporadaForm(forms.ModelForm):
    class Meta:
        model = Temporada
        fields = [
            'tipo', 'data_inicio', 'data_fim', 'cliente',
            'horario_chegada_equipe', 'horario_saida_equipe',
            'numero_diarias', 'tem_embarque', 'tem_desembarque', 'tem_ajuda_custo'
        ]
        labels = {
            'tipo': 'Tipo de Temporada',
            'data_inicio': 'Data de Início',
            'data_fim': 'Data de Fim',
            'cliente': 'Cliente',
            'horario_chegada_equipe': 'Horário Chegada da Equipe',
            'horario_saida_equipe': 'Horário Saída da Equipe',
            'numero_diarias': 'Número de Diárias',
            'tem_embarque': 'Tem Embarque',
            'tem_desembarque': 'Tem Desembarque',
            'tem_ajuda_custo': 'Tem Ajuda de Custo',
        }
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cliente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do cliente'}),
            'horario_chegada_equipe': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'horario_saida_equipe': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'numero_diarias': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.1', 
                'min': '0.1',
                'placeholder': 'Ex: 3.5'
            }),
            'tem_embarque': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tem_desembarque': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tem_ajuda_custo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'numero_diarias': 'Para Day Use, será automaticamente 1.0. Para outros tipos, pode ser fracionado (ex: 3.5)',
            'tem_embarque': 'Marque se esta temporada inclui remuneração de embarque',
            'tem_desembarque': 'Marque se esta temporada inclui remuneração de desembarque',
            'tem_ajuda_custo': 'Marque se esta temporada inclui ajuda de custo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Se for Day Use, definir número de diárias como 1.0 automaticamente
        if self.instance and self.instance.tipo == 'dayuse':
            self.fields['numero_diarias'].initial = 1.0
            self.fields['numero_diarias'].widget.attrs['readonly'] = True
            
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        numero_diarias = cleaned_data.get('numero_diarias')
        
        # Para Day Use, forçar número de diárias = 1.0
        if tipo == 'dayuse':
            cleaned_data['numero_diarias'] = 1.0
            
        return cleaned_data
