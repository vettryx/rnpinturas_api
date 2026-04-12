"""
==============================================================================
Módulo: Formulários (Forms)
Caminho: apps/clients/forms.py
==============================================================================

Validação de dados de entrada e regras de negócio para criação e edição
de clientes via interface web tradicional (quando não usar DRF).
"""

import logging

from cities.models import City
from common.forms import AddressBaseForm, ContactBaseForm, NoteBaseForm
from django import forms
from django.forms import inlineformset_factory

from .models import Client, ClientAddress, ClientContact

logger = logging.getLogger(__name__)


class ClientForm(forms.ModelForm):
    name = forms.CharField(
        label="Nome / Razão Social",
        widget=forms.TextInput(
            attrs={
                "class": "apps-form-input",
                "placeholder": "Digite o Nome ou Razão Social",
                "autofocus": True,
            }
        ),
    )
    fantasy_name = forms.CharField(
        label="Nome Fantasia",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "apps-form-input",
                "placeholder": "Digite o Nome Fantasia (opcional)",
            }
        ),
    )
    person_type = forms.ChoiceField(
        label="Tipo de Pessoa",
        choices=Client.PESSOA_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "apps-form-input select2",
                "placeholder": "Selecione o Certificador",
            }
        ),
    )
    cpf_cnpj = forms.CharField(
        label="CPF ou CNPJ",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "apps-form-input cpf-cnpj-mask",
                "placeholder": "Digite o documento",
            }
        ),
    )
    rg_ie = forms.CharField(
        label="RG / Inscrição Estadual",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "apps-form-input",
                "placeholder": "Digite o RG ou IE",
            }
        ),
    )

    class Meta:
        model = Client
        fields = [
            "name",
            "fantasy_name",
            "person_type",
            "cpf_cnpj",
            "rg_ie",
            "idle",
            "notes",
        ]


class ClientAddressForm(AddressBaseForm, NoteBaseForm):
    """
    Herda toda a estrutura de endereço e performance do AddressBaseForm,
    mais o campo de observações do NoteBaseForm.
    """
    class Meta:
        model = ClientAddress
        fields = [
            "zip_code",
            "city",
            "street",
            "number",
            "complement",
            "district",
        ]


class ClientContactForm(ContactBaseForm, NoteBaseForm):
    """
    Herda estrutura de contato do ContactBaseForm e observações do NoteBaseForm.
    """
    class Meta:
        model = ClientContact
        fields = [
            "contact_type",
            "value",
            "notes",
        ]


# --- Definição dos FormSets ---
ClientAddressFormSet = inlineformset_factory(
    Client,
    ClientAddress,
    form=ClientAddressForm,
    extra=1,
    can_delete=True,
)

ClientContactFormSet = inlineformset_factory(
    Client,
    ClientContact,
    form=ClientContactForm,
    extra=1,
    can_delete=True,
)
