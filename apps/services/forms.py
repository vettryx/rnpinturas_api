"""
==============================================================================
Módulo: Formulários (Forms)
Caminho: apps/services/forms.py
==============================================================================

Validação de dados de entrada e regras de negócio para criação e edição
de serviços via interface web tradicional (quando não usar DRF).
"""

from common.forms import IdleBaseForm
from django import forms

from .models import Service


class ServiceForm(IdleBaseForm):
    name = forms.CharField(
        label="Nome do Serviço",
        widget=forms.TextInput(
            attrs={
                "class": "apps-form-input",
                "placeholder": "Digite o nome do serviço",
                "autofocus": True,
            }
        ),
    )

    default_price = forms.DecimalField(
        label="Preço Sugerido",
        max_digits=10,
        decimal_places=2,
        min_value=0.00,
        widget=forms.NumberInput(
            attrs={
                "class": "apps-form-input",
                "placeholder": "Digite o preço sugerido (opcional)",
            }
        ),
    )

    class Meta:
        model = Service
        fields = [
            "name",
            "default_price",
            "notes",
            "idle",
        ]
