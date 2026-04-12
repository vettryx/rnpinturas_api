"""
==============================================================================
Módulo: Administração (Admin)
Caminho: apps/services/admin.py
==============================================================================

Registra os modelos de serviços no painel administrativo
do Django para gerenciamento rápido via interface web.
"""

from django.contrib import admin

from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "idle")
    search_fields = ("name",)
    list_filter = ("idle",)
