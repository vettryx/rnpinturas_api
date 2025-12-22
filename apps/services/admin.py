# apps/services/apps.py

from django.contrib import admin
from .models import Service

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'idle')
    search_fields = ('name',)
    list_filter = ('idle',)
