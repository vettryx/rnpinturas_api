# apps/cities/models.py

from common.models import IdleBase
from django.db import models


class UF(IdleBase):
    """
    Estados / Unidades Federativas.
    """
    name = models.CharField(max_length=50, verbose_name="Nome")
    abbreviation = models.CharField(max_length=2, unique=True, verbose_name="Sigla")

    class Meta:
        verbose_name = "Estado (UF)"
        verbose_name_plural = "Estados (UF)"
        db_table = "uf"
        ordering = ['name']

    def __str__(self):
        return self.abbreviation


class City(IdleBase):
    """
    Cidades.
    """
    uf = models.ForeignKey(
        UF,
        on_delete=models.PROTECT,
        verbose_name="Estado",
        related_name="cities"
    )
    name = models.CharField(max_length=255, verbose_name="Nome")

    class Meta:
        verbose_name = "Cidade"
        verbose_name_plural = "Cidades"
        db_table = "uf_cities"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.uf.abbreviation}"
