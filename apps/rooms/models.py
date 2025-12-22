# apps/rooms/models.py

from django.db import models
from common.models import IdleBase

class Room(IdleBase):
    """
    Cadastro de Cômodos (Ex: Sala, Quarto, Cozinha, Fachada).
    """
    name = models.CharField(max_length=255, verbose_name="Nome do Cômodo")

    class Meta:
        verbose_name = "Cômodo"
        verbose_name_plural = "Cômodos"
        db_table = "rooms"
        ordering = ['name']

    def __str__(self):
        return self.name


class RoomPart(IdleBase):
    """
    Cadastro de Partes/Superfícies (Ex: Teto, Parede, Rodapé, Janela, Porta).
    Independente do cômodo, pois uma parede existe em qualquer lugar.
    """
    name = models.CharField(max_length=255, verbose_name="Nome da Parte")

    class Meta:
        verbose_name = "Parte do Cômodo"
        verbose_name_plural = "Partes do Cômodo"
        db_table = "room_parts"
        ordering = ['name']

    def __str__(self):
        return self.name
