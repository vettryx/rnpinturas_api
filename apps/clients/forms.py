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
from common.models import AuxContactType
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
    notes = forms.CharField(
        label="Observações",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "apps-form-input",
                "placeholder": "Observações gerais sobre o cliente",
                "rows": 3,
            }
        ),
    )
    idle = forms.TypedChoiceField(
        label="Cliente Inativo?",
        choices=Client.SIM_NAO,
        coerce=lambda x: x == "True" or x is True,
        widget=forms.Select(
            attrs={
                "class": "apps-form-input select2",
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


class ClientAddressForm(forms.ModelForm):
    zip_code = forms.CharField(
        label="CEP",
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
        widget=forms.TextInput(
            attrs={
                "class": "apps-form-input logradouro-input",
                "placeholder": "Digite o Logradouro",
            }
        ),
    )
    number = forms.CharField(
        label="Número",
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
        widget=forms.TextInput(
            attrs={
                "class": "apps-form-input bairro-input",
                "placeholder": "Digite o Bairro",
            }
        ),
    )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # LÓGICA DE PERFORMANCE OTIMIZADA
        # Descobre o nome exato do campo no request.POST (trata standalone e formsets)
        city_field_name = f"{self.prefix}-city" if self.prefix else "city"

        if self.data and city_field_name in self.data:
            # 1. Requisição POST: O usuário tentou salvar algo
            try:
                city_id = int(self.data.get(city_field_name))
                self.fields["city"].queryset = City.objects.filter(pk=city_id)
            except (ValueError, TypeError):
                logger.debug(f"Input inválido no campo city: {self.data.get(city_field_name)}")
        elif self.instance and self.instance.pk and self.instance.city_id:
            # 2. Requisição GET (Edição): O cliente já tem uma cidade salva
            self.fields["city"].queryset = City.objects.filter(pk=self.instance.city_id)


class ClientContactForm(forms.ModelForm):
    contact_type = forms.ModelChoiceField(
        label="Tipo de Contato",
        queryset=AuxContactType.objects.filter(idle=False).order_by("name"),
        widget=forms.Select(
            attrs={
                "class": "apps-form-input select2",
                "id": "client-contact-type",
                "placeholder": "Selecione o Tipo de Contato",
            }
        ),
    )
    value = forms.CharField(
        label="Valor (Tel/Email)",
        widget=forms.TextInput(
            attrs={
                "class": "apps-form-input",
                "id": "client-contact-value",
                "placeholder": "Digite o Valor do Contato",
            }
        ),
    )
    notes = forms.CharField(
        label="Observações",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "apps-form-input",
                "id": "client-contact-notes",
                "placeholder": "Observações sobre o contato",
                "rows": 3,
            }
        ),
    )

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
