# apps/orders/admin.py

from django.contrib import admin
from .models import Order, OrderMaterial, OrderService

class OrderMaterialInline(admin.TabularInline):
    model = OrderMaterial
    extra = 1

class OrderServiceInline(admin.TabularInline):
    model = OrderService
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'issue_date', 'status')
    list_filter = ('status', 'issue_date')
    search_fields = ('client__name',)
    inlines = [OrderMaterialInline, OrderServiceInline]
