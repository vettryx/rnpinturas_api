"""
==============================================================================
Módulo: Formulários (Forms)
Caminho: apps/rooms/forms.py
==============================================================================

Validação de dados de entrada e regras de negócio para criação e edição
de cômodos via interface web tradicional (quando não usar DRF).
"""

from common.forms import IdleBaseForm
from django import forms

from .models import Room, RoomPart


class RoomForm(IdleBaseForm):
    name = forms.CharField(
        label="Nome do Cômodo",
        widget=forms.TextInput(
            attrs={
                "class": "apps-form-input",
                "placeholder": "Digite o nome do cômodo",
                "autofocus": True,
            }
        ),
    )

    class Meta:
        model = Room
        fields = [
            "name",
            "notes",
            "idle",
        ]


class RoomPartForm(IdleBaseForm):
    name = forms.CharField(
        label="Nome da Parte do Cômodo",
        widget=forms.TextInput(
            attrs={
                "class": "apps-form-input",
                "placeholder": "Digite o nome da parte do cômodo",
                "autofocus": True,
            }
        ),
    )

    class Meta:
        model = RoomPart
        fields = [
            "name",
            "notes",
            "idle",
        ]
