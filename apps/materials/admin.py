# apps/materials/admin.py

from django.contrib import admin
from .models import Material

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'idle')
    search_fields = ('name',)
    list_filter = ('idle',)
