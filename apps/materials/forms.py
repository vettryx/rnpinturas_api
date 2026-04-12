"""
==============================================================================
Módulo: Formulários (Forms)
Caminho: apps/materials/forms.py
==============================================================================

Validação de dados de entrada e regras de negócio para criação e edição
de materiais via interface web tradicional (quando não usar DRF).
"""

from common.forms import IdleBaseForm
from django import forms

from .models import Material


class MaterialForm(IdleBaseForm):
    name = forms.CharField(
        label="Nome do Material",
        widget=forms.TextInput(
            attrs={
                "class": "apps-form-input",
                "placeholder": "Digite o nome do material",
                "autofocus": True,
            }
        ),
    )
    default_price = forms.DecimalField(
        label="Preço Padrão",
        max_digits=10,
        decimal_places=2,
        initial=0.00,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "apps-form-input",
                "placeholder": "Digite o preço sugerido (opcional)",
            }
        ),
    )

    class Meta:
        model = Material
        fields = [
            "name",
            "default_price",
            "notes",
            "idle",
        ]
