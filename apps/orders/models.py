# apps/orders/models.py

from django.db import models
from common.models import NoteBase, AuxStatus, AuxUnitMeasure
from clients.models import Client
from materials.models import Material
from services.models import Service
from rooms.models import Room, RoomPart

class Order(NoteBase):
    """
    Tabela: orders
    """
    client = models.ForeignKey(Client, on_delete=models.PROTECT, verbose_name="Cliente")
    issue_date = models.DateField(blank=True, null=True, verbose_name="Data de Emissão")
    due_date = models.DateField(blank=True, null=True, verbose_name="Data de Vencimento")
    lead_time = models.IntegerField(blank=True, null=True, verbose_name="Prazo (Dias)")
    status = models.ForeignKey(AuxStatus, on_delete=models.PROTECT, verbose_name="Status")

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        db_table = "orders"

    def __str__(self):
        return f"Pedido {self.id} - {self.client}"


class OrderMaterial(NoteBase):
    """
    Tabela: orders_materials
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="materials", verbose_name="Pedido")
    material = models.ForeignKey(Material, on_delete=models.PROTECT, verbose_name="Material")
    unit_measure = models.ForeignKey(AuxUnitMeasure, on_delete=models.PROTECT, verbose_name="Unidade Medida")
    quantity = models.IntegerField(default=0, verbose_name="Quantidade")

    class Meta:
        verbose_name = "Material do Pedido"
        verbose_name_plural = "Materiais do Pedido"
        db_table = "orders_materials"

    def __str__(self):
        return f"{self.material} ({self.quantity})"


class OrderService(NoteBase):
    """
    Tabela: orders_services
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="services", verbose_name="Pedido")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, verbose_name="Serviço")
    room = models.ForeignKey(Room, on_delete=models.PROTECT, verbose_name="Ambiente")
    room_part = models.ForeignKey(RoomPart, on_delete=models.PROTECT, verbose_name="Parte do Ambiente")
    
    quantity = models.IntegerField(default=0, verbose_name="Quantidade")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço")
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Desconto")

    class Meta:
        verbose_name = "Serviço do Pedido"
        verbose_name_plural = "Serviços do Pedido"
        db_table = "orders_services"

    def __str__(self):
        return f"{self.service} - {self.room}"
