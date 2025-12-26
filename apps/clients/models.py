# apps/clients/models.py

import re
import unicodedata

from common.models import AddressBase, ContactBase, IdleBase, NoteBase
from django.db import models
from django.db.models import Q


class Client(IdleBase):
    """
    Cadastro Principal de Clientes.
    Herda de IdleBase (Status Ativo/Inativo com Select).
    """
    PESSOA_CHOICES = [
        ('F', 'Pessoa Física'),
        ('J', 'Pessoa Jurídica'),
    ]

    name = models.CharField(
        max_length=255,
        verbose_name="Nome / Razão Social"
    )
    fantasy_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Nome Fantasia"
    )
    person_type = models.CharField(
        max_length=1,
        choices=PESSOA_CHOICES,
        default='F',
        verbose_name="Tipo de Pessoa"
    )
    cpf_cnpj = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="CPF/CNPJ"
    )
    rg_ie = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="RG / Inscrição Estadual"
    )

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        db_table = "clients"
        ordering = ['name']

    constraints = [
            models.UniqueConstraint(
                fields=['cpf_cnpj'],
                condition=Q(cpf_cnpj__isnull=False) & ~Q(cpf_cnpj=""),
                name='unique_cpf_cnpj_not_null'
            )
        ]

    def save(self, *args, **kwargs):
        # Garante que o nome seja salvo em caixa alta
        if self.name:
            normalized = unicodedata.normalize('NFKD', self.name)
            clean_name = normalized.encode('ASCII', 'ignore').decode('utf-8')
            self.name = clean_name.strip().upper()

        if self.fantasy_name:
            normalized_fantasy = unicodedata.normalize('NFKD', self.fantasy_name)
            clean_fantasy = normalized_fantasy.encode('ASCII', 'ignore').decode('utf-8')
            self.fantasy_name = clean_fantasy.strip().upper()

        # Limpeza de CPF/CNPJ (Mantém apenas números)
        if self.cpf_cnpj:
            self.cpf_cnpj = re.sub(r'[^0-9]', '', self.cpf_cnpj)

        # Limpeza de RG/IE (Remove pontos, traços e barras)
        if self.rg_ie:
            self.rg_ie = re.sub(r'[\.\-\/]', '', self.rg_ie).strip().upper()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ClientAddress(NoteBase, AddressBase):
    """
    Endereços do Cliente.
    Herda campos e lógica de AddressBase.
    Herda 'notes' de NoteBase.
    """
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name="Cliente"
    )

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"
        db_table = "clients_addresses"


class ClientContact(NoteBase, ContactBase):
    """
    Contatos do Cliente.
    Herda lógica de telefone/email de ContactBase.
    """
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="contacts",
        verbose_name="Cliente"
    )

    class Meta:
        verbose_name = "Contato"
        verbose_name_plural = "Contatos"
        db_table = "clients_contacts"
