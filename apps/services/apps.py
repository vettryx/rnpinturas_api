"""
==============================================================================
Módulo: Configuração do App (App Config)
Caminho: apps/services/apps.py
==============================================================================

Arquivo de configuração central do aplicativo 'services'.
Define o nome, o campo de ID padrão e como ele aparece no painel admin.
"""

from django.apps import AppConfig


class ServicesConfig(AppConfig):
    name = "services"
    verbose_name = "Gestão de Serviços"
