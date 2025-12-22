# apps/rooms/admin.py

from django.contrib import admin
from .models import Room, RoomPart

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'idle')
    search_fields = ('name',)
    list_filter = ('idle',)

@admin.register(RoomPart)
class RoomPartAdmin(admin.ModelAdmin):
    list_display = ('name', 'idle')
    search_fields = ('name',)
    list_filter = ('idle',)
