# apps/common/admin.py

from django.contrib import admin
from .models import AuxContactType, AuxStatus, AuxUnitMeasure

@admin.register(AuxContactType)
class AuxContactTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'idle')
    search_fields = ('name',)
    list_filter = ('idle',)

@admin.register(AuxStatus)
class AuxStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'idle')
    search_fields = ('name',)
    list_filter = ('idle',)

@admin.register(AuxUnitMeasure)
class AuxUnitMeasureAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'idle')
    search_fields = ('code', 'name')
    list_filter = ('idle',)
