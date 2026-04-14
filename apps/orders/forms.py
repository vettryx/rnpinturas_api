"""
==============================================================================
Módulo: Formulários (Forms)
Caminho: apps/orders/forms.py
==============================================================================

Validação de dados de entrada e regras de negócio para criação e edição
de pedidos (orçamentos/OS) via interface web tradicional.
"""

from clients.models import Client
from common.forms import NoteBaseForm
from common.models import AuxStatus, AuxUnitMeasure
from django import forms
from django.forms import inlineformset_factory
from materials.models import Material
from rooms.models import Room, RoomPart
from services.models import Service

from .models import Order, OrderMaterial, OrderService


class OrderForm(forms.ModelForm):
    status = forms.ModelChoiceField(
        label="Status do Pedido",
        queryset=AuxStatus.objects.filter(idle=False).order_by("name"),
        widget=forms.Select(
            attrs={
                "class": "apps-form-input select2",
                "placeholder": "Selecione o Status do Pedido",
            }
        ),
    )
    issue_date = forms.DateField(
        label="Data de Emissão",
        widget=forms.DateInput(
            attrs={
                "class": "apps-form-input",
                "type": "date",
                "placeholder": "Digite a Data de Emissão",
                "autofocus": True,
            }
        ),
    )
    validity_days = forms.IntegerField(
        label="Validade (Dias)",
        initial=7,
        widget=forms.NumberInput(
            attrs={
                "class": "apps-form-input",
                "placeholder": "Digite a validade do pedido em dias (ex: 7)",
            }
        ),
    )
    due_date = forms.DateField(
        label="Data de Vencimento",
        widget=forms.DateInput(
            attrs={
                "class": "apps-form-input",
                "type": "date",
                "placeholder": "Digite a data de vencimento do pedido",
            }
        ),
    )
    lead_time = forms.IntegerField(
        label="Prazo Médio de Conclusão ( em dias)",
        widget=forms.NumberInput(
            attrs={
                "class": "apps-form-input",
                "placeholder": "Digite o prazo médio de conclusão do pedido em dias (ex: 30)",
            }
        ),
    )
    client = forms.ModelChoiceField(
        label="Cliente",
        queryset=Client.objects.filter(idle=False).order_by("name"),
        widget=forms.Select(
            attrs={
                "class": "apps-form-input select2",
                "placeholder": "Selecione o Cliente",
            }
        ),
    )


    class Meta:
        model = Order
        fields = [
            "client",
            "status",
            "issue_date",
            "validity_days",
            "due_date",
            "lead_time",
            "notes",
        ]


class OrderMaterialForm(NoteBaseForm):
    """
    Herda o campo de observações do NoteBaseForm.
    """
    material = forms.ModelChoiceField(
        label="Material",
        queryset=Material.objects.filter(idle=False).order_by("name"),
        widget=forms.Select(
            attrs={
                "class": "apps-form-input select2",
                "placeholder": "Selecione o Material",
                "autofocus": True,
            }
        ),
    )
    unit_measure = forms.ModelChoiceField(
        label="Unidade de Medida",
        queryset=AuxUnitMeasure.objects.filter(idle=False).order_by("name"),
        widget=forms.Select(
            attrs={
                "class": "apps-form-input select2",
                "placeholder": "Selecione a Unidade de Medida",
            }
        ),
    )
    quantity = forms.DecimalField(
        label="Quantidade",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "apps-form-input",
                "placeholder": "Digite a quantidade",
            }
        ),
    )
    price = forms.DecimalField(
        label="Preço Unitário",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "apps-form-input",
                "placeholder": "Digite o preço unitário",
            }
        ),
    )
    discount = forms.DecimalField(
        label="Desconto",
        max_digits=10,
        decimal_places=2,
        initial=0.00,
        widget=forms.NumberInput(
            attrs={
                "class": "apps-form-input",
                "placeholder": "Digite o desconto",
            }
        ),
    )

    class Meta:
        model = OrderMaterial
        fields = [
            "material",
            "unit_measure",
            "quantity",
            "price",
            "discount",
            "notes",
        ]


class OrderServiceForm(NoteBaseForm):
    """
    Herda o campo de observações do NoteBaseForm.
    """
    service = forms.ModelChoiceField(
        label="Serviço",
        queryset=Service.objects.filter(idle=False).order_by("name"),
        widget=forms.Select(
            attrs={
                "class": "apps-form-input select2",
                "placeholder": "Selecione o Serviço",
                "autofocus": True,
            }
        ),
    )
    room = forms.ModelChoiceField(
        label="Ambiente",
        queryset=Room.objects.filter(idle=False).order_by("name"),
        widget=forms.Select(
            attrs={
                "class": "apps-form-input select2",
                "placeholder": "Selecione o Ambiente",
            }
        ),
    )
    room_part = forms.ModelChoiceField(
        label="Parte do Ambiente",
        queryset=RoomPart.objects.filter(idle=False).order_by("name"),
        widget=forms.Select(
            attrs={
                "class": "apps-form-input select2",
                "placeholder": "Selecione a Parte do Ambiente",
            }
        ),
    )
    quantity = forms.DecimalField(
        label="Quantidade",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "apps-form-input",
                "placeholder": "Digite a quantidade",
            }
        ),
    )
    price = forms.DecimalField(
        label="Preço Unitário",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "apps-form-input",
                "placeholder": "Digite o preço unitário",
            }
        ),
    )
    discount = forms.DecimalField(
        label="Desconto",
        max_digits=10,
        decimal_places=2,
        initial=0.00,
        widget=forms.NumberInput(
            attrs={
                "class": "apps-form-input",
                "placeholder": "Digite o desconto",
            }
        ),
    )

    class Meta:
        model = OrderService
        fields = [
            "service",
            "room",
            "room_part",
            "quantity",
            "price",
            "discount",
            "notes",
        ]


# --- Definição dos FormSets ---
OrderMaterialFormSet = inlineformset_factory(
    Order,
    OrderMaterial,
    form=OrderMaterialForm,
    extra=1,
    can_delete=True,
)

OrderServiceFormSet = inlineformset_factory(
    Order,
    OrderService,
    form=OrderServiceForm,
    extra=1,
    can_delete=True,
)
