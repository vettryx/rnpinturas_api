# apps/cities/admin.py

from django.contrib import admin
from .models import UF, City

@admin.register(UF)
class UFAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'name', 'idle')
    search_fields = ('name', 'abbreviation')
    list_filter = ('idle',)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'uf', 'idle')
    search_fields = ('name',)
    list_filter = ('uf', 'idle')
    autocomplete_fields = ['uf']
