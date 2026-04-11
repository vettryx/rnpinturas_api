"""
==============================================================================
Módulo: Administração (Admin)
Caminho: apps/clients/admin.py
==============================================================================

Registra os modelos de clientes e contatos no painel administrativo
do Django para gerenciamento rápido via interface web.
"""

from django.contrib import admin
from django.db import models
from django.forms import Textarea

from .models import Client, ClientAddress, ClientContact


class ClientContactInline(admin.TabularInline):
    """
    Permite adicionar contatos diretamente na tela do Cliente.
    """
    model = ClientContact
    extra = 1
    classes = ['collapse']
    fields = ('contact_type', 'value', 'notes')
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 40})},
    }

class ClientAddressInline(admin.StackedInline):
    """
    Permite adicionar endereços na tela do Cliente.
    """
    model = ClientAddress
    extra = 0
    autocomplete_fields = ['city']
    classes = ['collapse']
    fields = (
        'zip_code',
        'street',
        'number',
        'complement',
        'district',
        'city',
        'notes'
    )
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3})},
    }

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'person_type', 'cpf_cnpj', 'idle')
    search_fields = ('name', 'fantasy_name', 'cpf_cnpj')
    list_filter = ('person_type', 'idle')

    # Adiciona os formulários filhos dentro do formulário pai
    inlines = [ClientContactInline, ClientAddressInline]

    fieldsets = (
        ('Dados Principais', {
            'fields': ('name', 'fantasy_name', 'person_type', 'idle')
        }),
        ('Documentação', {
            'fields': ('cpf_cnpj', 'rg_ie')
        }),
        ('Observações', {
            'fields': ('notes',),
            'classes': ('collapse',),
        }),
    )
