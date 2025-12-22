# apps/materials/models.py

from django.db import models
from common.models import IdleBase

class Material(IdleBase):
    """
    Cadastro de Materiais (Tintas, Insumos, Ferramentas).
    """
    name = models.CharField(max_length=255, verbose_name="Nome do Material")

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materiais"
        db_table = "materials"
        ordering = ['name']

    def __str__(self):
        return self.name
