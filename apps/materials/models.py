# apps/materials/models.py

from common.models import IdleBase
from django.db import models


class Material(IdleBase):
    """
    Cadastro de Materiais (Tintas, Insumos, Ferramentas).
    """

    name = models.CharField(max_length=255, verbose_name="Nome do Material")
    default_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço Padrão"
    )

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materiais"
        db_table = "materials"
        ordering = ["name"]

    def __str__(self):
        return self.name
