"""
==============================================================================
Módulo: Configuração do App (App Config)
Caminho: apps/clients/apps.py
==============================================================================

Arquivo de configuração central do aplicativo 'clients'.
Define o nome, o campo de ID padrão e como ele aparece no painel admin.
"""

from django.apps import AppConfig


class ClientsConfig(AppConfig):
    name = "clients"
    hub_name = "Clientes"
    verbose_name = "Gestão de Clientes"
    icon = "group"
