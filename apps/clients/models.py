"""
==============================================================================
Módulo: Modelos de Clientes (Clients Models)
Caminho: apps/clients/models.py
==============================================================================

Define a entidade central de clientes (Customer) da RN Pinturas,
incluindo seus dados de faturamento, contatos e endereços.
"""

import re
import unicodedata

from common.models import AddressBase, ContactBase, IdleBase, NoteBase
from django.contrib import admin
from django.db import models
from django.db.models import Max, Q


class Client(IdleBase):
    """
    Cadastro Principal de Clientes.
    Herda de IdleBase (Status Ativo/Inativo com Select).
    """

    PESSOA_CHOICES = [
        ("F", "Pessoa Física"),
        ("J", "Pessoa Jurídica"),
    ]

    name = models.CharField(max_length=255, verbose_name="Nome / Razão Social")
    fantasy_name = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Nome Fantasia"
    )
    person_type = models.CharField(
        max_length=1, choices=PESSOA_CHOICES, default="F", verbose_name="Tipo de Pessoa"
    )
    cpf_cnpj = models.CharField(max_length=20, blank=True, null=True, verbose_name="CPF/CNPJ")
    rg_ie = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="RG / Inscrição Estadual"
    )

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        db_table = "clients"
        ordering = ["name"]

    constraints = [
        models.UniqueConstraint(
            fields=["cpf_cnpj"],
            condition=Q(cpf_cnpj__isnull=False) & ~Q(cpf_cnpj=""),
            name="unique_cpf_cnpj_not_null",
        )
    ]

    def save(self, *args, **kwargs):
        # 1. Geração automática do ID caso esteja vazio
        if not self.id:
            # Busca o maior uid atualmente cadastrado na tabela
            max_id = Client.objects.aggregate(Max("id"))["id__max"]
            # Se não existir nenhum cliente ainda, começa do 1, senão soma 1 ao maior
            self.id = (max_id or 0) + 1

        # 2. Garante que o nome seja salvo em caixa alta e sem acentos
        if self.name:
            normalized = unicodedata.normalize("NFKD", self.name)
            clean_name = normalized.encode("ASCII", "ignore").decode("utf-8")
            self.name = clean_name.strip().upper()

        if self.fantasy_name:
            normalized_fantasy = unicodedata.normalize("NFKD", self.fantasy_name)
            clean_fantasy = normalized_fantasy.encode("ASCII", "ignore").decode("utf-8")
            self.fantasy_name = clean_fantasy.strip().upper()

        # 3. Limpeza de CPF/CNPJ (Mantém apenas números)
        if self.cpf_cnpj:
            self.cpf_cnpj = re.sub(r"[^0-9]", "", self.cpf_cnpj)

        # 4. Limpeza de RG/IE (Remove pontos, traços e barras)
        if self.rg_ie:
            self.rg_ie = re.sub(r"[\.\-\/]", "", self.rg_ie).strip().upper()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.id_formatted}] {self.name}"

    @property
    @admin.display(description="ID", ordering="id")
    def id_formatted(self):
        """
        Retorna o ID formatado com no mínimo 6 dígitos e separador (ex: 000.011).
        Ideal para usar em templates e painéis administrativos.
        """
        if not self.id:
            return "000.000"

        id_str = f"{self.id:06d}"
        return f"{id_str[:-3]}.{id_str[-3:]}"


class ClientAddress(NoteBase, AddressBase):
    """
    Endereços do Cliente.
    Herda campos e lógica de AddressBase.
    Herda 'notes' de NoteBase.
    """

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="addresses", verbose_name="Cliente"
    )

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"
        db_table = "clients_addresses"

    @property
    def formatted_address(self):
        """
        Retorna o endereço formatado de forma inteligente, 
        ignorando campos em branco e evitando vírgulas soltas.
        """
        parts = [
            self.street,
            self.number,
            self.district,
            self.city.name if self.city else None,
            self.city.uf.abbreviation if self.city and hasattr(self.city, 'uf') and self.city.uf else None,
            f"CEP: {self.zip_code}" if self.zip_code else None
        ]

        # Filtra a lista mantendo apenas os itens que têm algum texto válido
        valid_parts = [str(p).strip() for p in parts if p and str(p).strip()]

        return ", ".join(valid_parts) if valid_parts else "Endereço não informado"


class ClientContact(NoteBase, ContactBase):
    """
    Contatos do Cliente.
    Herda lógica de telefone/email de ContactBase.
    """

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="contacts", verbose_name="Cliente"
    )

    class Meta:
        verbose_name = "Contato"
        verbose_name_plural = "Contatos"
        db_table = "clients_contacts"
