"""
==============================================================================
Módulo: Modelos de Pedidos (Orders Models)
Caminho: apps/orders/models.py
==============================================================================

Define a entidade central de pedidos (Order) da RN Pinturas
e suas relações com materiais e serviços.
"""

from clients.models import Client
from common.models import AuxStatus, AuxUnitMeasure, NoteBase
from django.db import models
from materials.models import Material
from rooms.models import Room, RoomPart
from services.models import Service


class Order(NoteBase):
    """
    Cadastro de Pedidos (Ex: Orçamento, Ordem de Serviço).
    Tabela: orders
    """

    # Constante para o linter (4 do ano + min 1 da sequência)
    MIN_CODE_LENGTH = 5

    order_code = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        verbose_name="Código do Pedido"
    )
    client = models.ForeignKey(Client, on_delete=models.PROTECT, verbose_name="Cliente")
    issue_date = models.DateField(blank=True, null=True, verbose_name="Data de Emissão")
    due_date = models.DateField(blank=True, null=True, verbose_name="Data de Vencimento")
    lead_time = models.IntegerField(blank=True, null=True, verbose_name="Prazo (Dias)")
    status = models.ForeignKey(AuxStatus, on_delete=models.PROTECT, verbose_name="Status")

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        db_table = "orders"
        ordering = ["-issue_date", "-id"]

    @property
    def formatted_code(self):
        """Retorna o código formatado para o usuário: 2025-0001"""
        if self.order_code and len(self.order_code) >= self.MIN_CODE_LENGTH:
            ano = self.order_code[:4]
            sequencial = self.order_code[4:]
            return f"{ano}-{sequencial}"
        return self.order_code

    def __str__(self):
        return f"{self.formatted_code} - {self.client}"

    def save(self, *args, **kwargs):
        # Geração do Código Sequencial Anual (Bruto: 20250001)
        if not self.order_code:
            current_year = self.issue_date.year
            last_order = Order.objects.filter(issue_date__year=current_year).order_by('id').last()

            if last_order and last_order.order_code:
                # Pega do 5º caractere em diante e converte pra somar
                last_sequence = int(last_order.order_code[4:])
                new_sequence = last_sequence + 1
            else:
                new_sequence = 1

            # Salva sem o hífen: 20250001
            self.order_code = f"{current_year}{new_sequence:04d}"

        super().save(*args, **kwargs)


class OrderMaterial(NoteBase):
    """
    Tabela: orders_materials
    """
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="materials", verbose_name="Pedido"
    )
    material = models.ForeignKey(Material, on_delete=models.PROTECT, verbose_name="Material")
    unit_measure = models.ForeignKey(
        AuxUnitMeasure, on_delete=models.PROTECT, verbose_name="Unidade Medida"
    )
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name="Quantidade"
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço Unitário"
    )
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name="Desconto"
    )

    @property
    def total_price(self):
        return (self.quantity * self.price) - self.discount

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
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="services", verbose_name="Pedido"
    )
    service = models.ForeignKey(Service, on_delete=models.PROTECT, verbose_name="Serviço")
    room = models.ForeignKey(Room, on_delete=models.PROTECT, verbose_name="Ambiente")
    room_part = models.ForeignKey(
        RoomPart, on_delete=models.PROTECT, verbose_name="Parte do Ambiente"
    )

    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name="Quantidade"
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço Unitário"
    )
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name="Desconto"
    )

    @property
    def total_price(self):
        return (self.quantity * self.price) - self.discount

    class Meta:
        verbose_name = "Serviço do Pedido"
        verbose_name_plural = "Serviços do Pedido"
        db_table = "orders_services"

    def __str__(self):
        return f"{self.service} - {self.room}"
