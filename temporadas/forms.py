from django import forms
from .models import Temporada

class TemporadaForm(forms.ModelForm):
    class Meta:
        model = Temporada
        fields = ['nome', 'data_inicio', 'data_fim', 'cliente', 'tipo']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
        }

class TemporadaForm(forms.ModelForm):
    class Meta:
        model = Temporada
        fields = ['nome', 'data_inicio', 'data_fim', 'cliente', 'tipo']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cliente': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
        }
