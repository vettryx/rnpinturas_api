"""
==============================================================================
Módulo: Configuração do App (App Config)
Caminho: apps/materials/apps.py
==============================================================================

Arquivo de configuração central do aplicativo 'materials'.
Define o nome, o campo de ID padrão e como ele aparece no painel admin.
"""

from django.apps import AppConfig


class MaterialsConfig(AppConfig):
    name = "materials"
    hub_name = "Materiais"
    verbose_name = "Materiais necessários para a execução dos serviços"
    icon = "inventory_2"
