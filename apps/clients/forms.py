# apps/clients/forms.py

"""
Definição dos formulários do aplicativo 'clients'.
"""

from django import forms
from django.forms import inlineformset_factory

from .models import Client, ClientAddress, ClientContact
from cities.models import City
from common.models import AuxContactType


class ClientForm(forms.ModelForm):
    name = forms.CharField(
        label="Nome / Razão Social",
        widget=forms.TextInput(
            attrs={
                "class": "apps-form-input",
                "id": "client-name",
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
                "id": "client-fantasy-name",
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
                "id": "client-person-type",
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
                "id": "client-cpf-cnpj",
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
                "id": "client-rg-ie",
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
                "id": "client-notes",
                "placeholder": "Observações gerais sobre o cliente",
                "rows": 3,
            }
        ),
    )
    idle = forms.TypedChoiceField(
        label="Cliente Inativo?",
        choices=Client.SIM_NAO, 
        coerce=lambda x: x == 'True' or x is True,
        widget=forms.Select(
            attrs={
                "class": "apps-form-input select2",
                "id": "client-idle",
            }
        ),
    )

    class Meta:
        model = Client
        fields = [
            'name',
            'fantasy_name',
            'person_type',
            'cpf_cnpj',
            'rg_ie',
            'idle',
            'notes',
        ]


class ClientAddressForm(forms.ModelForm):
    zip_code = forms.CharField(
        label="CEP",
        widget=forms.TextInput(
            attrs={
                "class": "apps-form-input zip-code-input zip-code-mask",
                "id": "client-address-zip-code",
                "placeholder": "Digite o CEP",
            }
        ),
    )
    city = forms.ModelChoiceField(
        label="Cidade",
        queryset=City.objects.all().order_by('name'),
        widget=forms.Select(
            attrs={
                "class": "apps-form-input select2-ajax",
                "data-ajax-url": "/cities/api/autocomplete/",
                "id": "client-address-city",
                "placeholder": "Selecione a Cidade",
            }
        ),
    )
    street = forms.CharField(
        label="Logradouro (Rua/Av)",
        widget=forms.TextInput(
            attrs={
                "class": "apps-form-input",
                "id": "client-address-street",
                "placeholder": "Digite o Logradouro",
            }
        ),
    )
    number = forms.CharField(
        label="Número",
        widget=forms.TextInput(
            attrs={
                "class": "apps-form-input",
                "id": "client-address-number",
                "placeholder": "Digite o Número",
            }
        ),
    )
    complement = forms.CharField(
        label="Complemento",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "apps-form-input",
                "id": "client-address-complement",
                "placeholder": "Digite o Complemento (opcional)",
            }
        ),
    )
    district = forms.CharField(
        label="Bairro",
        widget=forms.TextInput(
            attrs={
                "class": "apps-form-input",
                "id": "client-address-district",
                "placeholder": "Digite o Bairro",
            }
        ),
    )

    class Meta:
        model = ClientAddress
        fields = [
            'zip_code',
            'city',
            'street',
            'number',
            'complement',
            'district',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # LÓGICA DE PERFORMANCE (O Pulo do Gato)
        # Por padrão, queryset vazio para não renderizar 5000 options no HTML
        self.fields['city'].queryset = City.objects.none()

        # 1. Se tiver dados no POST (tentando salvar), carrega a cidade enviada para validar
        if 'city' in self.data:
            try:
                city_id = int(self.data.get('city'))
                self.fields['city'].queryset = City.objects.filter(pk=city_id)
            except (ValueError, TypeError):
                pass  # Input inválido, deixa vazio e o Django gerencia o erro field required
        
        # 2. Se for edição (instance já existe), carrega a cidade atual
        elif self.instance.pk and self.instance.city:
            self.fields['city'].queryset = City.objects.filter(pk=self.instance.city.pk)
        
        # 3. Formset Management (O prefixo muda em formsets: 'address_set-0-city')
        elif self.prefix:
             # Tenta achar o campo no POST usando o prefixo (ex: clients-address-0-city)
             field_name = f"{self.prefix}-city"
             if self.data and field_name in self.data:
                 try:
                     city_id = int(self.data.get(field_name))
                     self.fields['city'].queryset = City.objects.filter(pk=city_id)
                 except Exception:
                     pass



class ClientContactForm(forms.ModelForm):
    contact_type = forms.ModelChoiceField(
        label="Tipo de Contato",
        queryset=AuxContactType.objects.filter(idle=False).order_by('name'),
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
            'contact_type',
            'value',
            'notes',
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
