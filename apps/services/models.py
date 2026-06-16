"""
==============================================================================
Módulo: Modelos de Serviços (Services Models)
Caminho: apps/services/models.py
==============================================================================

Define a entidade central de serviços (Service) da RN Pinturas
"""

from common.models import IdleBase, PriceBase
from django.db import models


class Service(IdleBase, PriceBase):
    """
    Cadastro de Serviços (Ex: Pintura, Lixamento, Emassamento).
    """

    name = models.CharField(max_length=255, verbose_name="Nome do Serviço")
    default_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço Sugerido"
    )

    class Meta:
        verbose_name = "Serviço"
        verbose_name_plural = "Serviços"
        db_table = "services"
        ordering = ["name"]

    def __str__(self):
        return self.name
