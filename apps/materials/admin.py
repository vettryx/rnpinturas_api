"""
==============================================================================
Módulo: Administração (Admin)
Caminho: apps/materials/admin.py
==============================================================================

Registra os modelos de materiais no painel administrativo
do Django para gerenciamento rápido via interface web.
"""

from django.contrib import admin

from .models import Material


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("name", "idle")
    search_fields = ("name",)
    list_filter = ("idle",)
