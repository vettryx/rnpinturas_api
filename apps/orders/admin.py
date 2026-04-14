"""
==============================================================================
Módulo: Administração (Admin)
Caminho: apps/orders/admin.py
==============================================================================

Registra os modelos de pedidos e seus itens (materiais e serviços)
no painel administrativo do Django para gerenciamento rápido via interface web.
"""

from django.contrib import admin
from django.db import models
from django.forms import Textarea

from .models import Order, OrderMaterial, OrderService


class OrderMaterialInline(admin.TabularInline):
    """
    Permite adicionar materiais diretamente na tela do Pedido.
    """
    model = OrderMaterial
    extra = 1
    classes = ["collapse"]
    fields = ("material", "unit_measure", "quantity", "price", "discount", "notes")
    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 2, "cols": 40})},
    }


class OrderServiceInline(admin.TabularInline):
    """
    Permite adicionar serviços diretamente na tela do Pedido.
    """
    model = OrderService
    extra = 1
    classes = ["collapse"]
    fields = ("service", "room", "room_part", "quantity", "price", "discount", "notes")
    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 2, "cols": 40})},
    }


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Usamos o método customizado para exibir o código formatado (ex: 2025-0001)
    list_display = ("get_formatted_code", "client", "issue_date", "due_date", "status")
    search_fields = ("order_code", "client__name", "client__fantasy_name", "client__cpf_cnpj")
    list_filter = ("status", "issue_date", "due_date")

    # Cria uma barra de pesquisa inteligente para selecionar o cliente
    autocomplete_fields = ["client"]

    # Adiciona os formulários filhos dentro do formulário pai
    inlines = [OrderServiceInline, OrderMaterialInline]

    fieldsets = (
        ("Dados do Pedido", {
            "fields": ("order_code", "client", "status")
        }),
        ("Datas e Prazos", {
            "fields": ("issue_date", "validity_days", "due_date", "lead_time")
        }),
        ("Observações", {
            "fields": ("notes",),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="Código", ordering="order_code")
    def get_formatted_code(self, obj):
        """
        Garante que a listagem do admin exiba o código com o hífen (via property),
        mas ainda permita a ordenação correta usando o campo real 'order_code' do banco.
        """
        return obj.formatted_code
