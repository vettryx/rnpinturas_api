"""
==============================================================================
Módulo: Configuração do App (App Config)
Caminho: apps/rooms/apps.py
==============================================================================

Arquivo de configuração central do aplicativo 'rooms'.
Define o nome, o campo de ID padrão e como ele aparece no painel admin.
"""

from django.apps import AppConfig


class RoomsConfig(AppConfig):
    name = "rooms"
    hub_name = "Cômodos e Partes de Cômodos"
    verbose_name = "Gestão de Cômodos e Partes de Cômodos"
    icon = "other_houses"
