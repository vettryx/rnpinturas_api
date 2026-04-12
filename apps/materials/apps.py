"""
==============================================================================
Módulo: Configuração do App (App Config)
Caminho: apps/modules/apps.py
==============================================================================

Arquivo de configuração central do aplicativo 'modules'.
Define o nome, o campo de ID padrão e como ele aparece no painel admin.
"""

from django.apps import AppConfig


class MaterialsConfig(AppConfig):
    name = "materials"
    verbose_name = "Materiais necessários para a execução dos serviços"
