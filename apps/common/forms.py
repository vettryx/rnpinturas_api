"""
==============================================================================
Módulo: Formulários Comuns (Forms)
Caminho: apps/common/forms.py
==============================================================================

Moldes de formulários genéricos para serem herdados por outros apps,
garantindo padronização visual e de performance (DRY).
"""

import logging

from cities.models import City
from django import forms

from .models import AuxContactType

logger = logging.getLogger(__name__)


class NoteBaseForm(forms.ModelForm):
    """Molde genérico para formulários que possuem apenas Observações."""

    notes = forms.CharField(
        label="Observações",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "apps-form-input",
                "placeholder": "Observações gerais...",
                "rows": 3,
            }
        ),
    )


class IdleBaseForm(NoteBaseForm):
    """Molde genérico para formulários que possuem Observações e Status Inativo."""

    SIM_NAO = [
        (False, "Não"),
        (True, "Sim"),
    ]

    idle = forms.TypedChoiceField(
        label="Inativo?",
        choices=SIM_NAO,
        coerce=lambda x: x == "True" or x is True,
        widget=forms.Select(
            attrs={
                "class": "apps-form-input select2",
            }
        ),
    )


class AddressBaseForm(forms.ModelForm):
    """
    Molde genérico para Endereços.
    Já inclui a lógica de performance (Select2 AJAX) para não carregar
    milhares de cidades no HTML simultaneamente.
    """

    zip_code = forms.CharField(
        label="CEP",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "apps-form-input zip-code-input zip-code-mask cep-input",
                "placeholder": "Digite o CEP",
            }
        ),
    )
    city = forms.ModelChoiceField(
        label="Cidade",
        queryset=City.objects.none().order_by("name"),
        widget=forms.Select(
            attrs={
                "class": "apps-form-input select2-ajax city-input",
                "data-ajax-url": "/cities/api/autocomplete/",
                "placeholder": "Selecione a Cidade",
            }
        ),
    )
    street = forms.CharField(
        label="Logradouro (Rua/Av)",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "apps-form-input logradouro-input",
                "placeholder": "Digite o Logradouro",
            }
        ),
    )
    number = forms.CharField(
        label="Número",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "apps-form-input",
                "placeholder": "Digite o Número",
            }
        ),
    )
    complement = forms.CharField(
        label="Complemento",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "apps-form-input complemento-input",
                "placeholder": "Digite o Complemento (opcional)",
            }
        ),
    )
    district = forms.CharField(
        label="Bairro",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "apps-form-input bairro-input",
                "placeholder": "Digite o Bairro",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # LÓGICA DE PERFORMANCE OTIMIZADA PARA QUALQUER APP
        city_field_name = f"{self.prefix}-city" if self.prefix else "city"

        if self.data and city_field_name in self.data:
            try:
                city_id = int(self.data.get(city_field_name))
                self.fields["city"].queryset = City.objects.filter(pk=city_id)
            except (ValueError, TypeError):
                logger.debug(f"Input inválido no campo city: {self.data.get(city_field_name)}")
        elif (
            hasattr(self, "instance")
            and getattr(self.instance, "pk", None)
            and getattr(self.instance, "city_id", None)
        ):
            self.fields["city"].queryset = City.objects.filter(pk=self.instance.city_id)


class ContactBaseForm(forms.ModelForm):
    """Molde genérico para Contatos."""

    contact_type = forms.ModelChoiceField(
        label="Tipo de Contato",
        queryset=AuxContactType.objects.filter(idle=False).order_by("name"),
        widget=forms.Select(
            attrs={
                "class": "apps-form-input select2",
                "placeholder": "Selecione o Tipo de Contato",
            }
        ),
    )
    value = forms.CharField(
        label="Valor (Tel/Email)",
        widget=forms.TextInput(
            attrs={
                "class": "apps-form-input",
                "placeholder": "Digite o Valor do Contato",
            }
        ),
    )
