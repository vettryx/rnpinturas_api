"""
==============================================================================
Módulo: Formulários (Forms)
Caminho: apps/orders/forms.py
==============================================================================

Validação de dados de entrada e regras de negócio para criação e edição
de pedidos (orçamentos/OS) via interface web tradicional.
"""
from datetime import timedelta

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
            format="%Y-%m-%d",
            attrs={
                "class": "apps-form-input",
                "type": "date",
                "placeholder": "Digite a Data de Emissão",
                "autofocus": True,
            }
        ),
    )
    due_date = forms.DateField(
        label="Data de Vencimento",
        widget=forms.DateInput(
            format="%Y-%m-%d",
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
    validity_days = forms.IntegerField(
        label="Validade (Dias)",
        initial=7,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "apps-form-input",
                "id": "order-validity-days",
                "placeholder": "Ex: 7",
            }
        ),
    )


    class Meta:
        model = Order
        fields = [
            "client",
            "status",
            "issue_date",
            "due_date",
            "lead_time",
            "notes",
        ]

    def clean(self):
        """
        Intercepta os dados antes de salvar no banco para calcular a Data de Vencimento
        baseada nos dias de validade informados na tela.
        """
        cleaned_data = super().clean()
        issue_date = cleaned_data.get("issue_date")
        validity_days = cleaned_data.get("validity_days")
        due_date = cleaned_data.get("due_date")

        # Se o usuário informou a emissão e a validade, mas a data de vencimento está vazia
        if issue_date and validity_days and not due_date:
            cleaned_data["due_date"] = issue_date + timedelta(days=validity_days)

        return cleaned_data


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
