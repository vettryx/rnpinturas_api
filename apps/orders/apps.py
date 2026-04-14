"""
==============================================================================
Módulo: Configuração do App (App Config)
Caminho: apps/orders/apps.py
==============================================================================

Arquivo de configuração central do aplicativo 'orders'.
Define o nome, o campo de ID padrão e como ele aparece no painel admin.
"""
from django.apps import AppConfig


class OrdersConfig(AppConfig):
    name = "orders"
    verbose_name = "Gestão de Pedidos"
