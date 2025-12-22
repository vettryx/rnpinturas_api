# apps/services/models.py

from django.db import models
from common.models import IdleBase

class Service(IdleBase):
    """
    Cadastro de Serviços (Ex: Pintura, Lixamento, Emassamento).
    """
    name = models.CharField(max_length=255, verbose_name="Nome do Serviço")

    class Meta:
        verbose_name = "Serviço"
        verbose_name_plural = "Serviços"
        db_table = "services"
        ordering = ['name']

    def __str__(self):
        return self.name
