# apps/clients/admin.py

from django.contrib import admin
from .models import Client, ClientAddress, ClientContact

class ClientContactInline(admin.TabularInline):
    """
    Permite adicionar contatos diretamente na tela do Cliente.
    TabularInline deixa os campos um ao lado do outro (mais compacto).
    """
    model = ClientContact
    extra = 1  # Quantas linhas vazias aparecem por padrão
    classes = ['collapse'] # Permite esconder/mostrar a seção

class ClientAddressInline(admin.StackedInline):
    """
    Permite adicionar endereços na tela do Cliente.
    StackedInline empilha os campos (melhor para formulários grandes como endereço).
    """
    model = ClientAddress
    extra = 0
    autocomplete_fields = ['city']  # Busca inteligente de cidade (Requer configuração no CityAdmin)
    classes = ['collapse']

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
