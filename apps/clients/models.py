# apps/clients/models.py

from django.db import models
from common.models import IdleBase, NoteBase, AuxContactType
from cities.models import City

class Client(IdleBase):
    """
    Cadastro Principal de Clientes.
    Herda de IdleBase (Status Ativo/Inativo com Select).
    """
    PESSOA_CHOICES = [
        ('F', 'Pessoa Física'),
        ('J', 'Pessoa Jurídica'),
    ]

    name = models.CharField(max_length=255, verbose_name="Nome / Razão Social")
    fantasy_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome Fantasia")
    
    person_type = models.CharField(
        max_length=1, 
        choices=PESSOA_CHOICES, 
        default='F', 
        verbose_name="Tipo de Pessoa"
    )
    
    cpf_cnpj = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="CPF/CNPJ")
    rg_ie = models.CharField(max_length=20, blank=True, null=True, verbose_name="RG / Inscrição Estadual")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        db_table = "clients"
        ordering = ['name']

    def __str__(self):
        return self.name


class ClientAddress(NoteBase):
    """
    Endereços do Cliente.
    """
    client = models.ForeignKey(
        Client, 
        on_delete=models.CASCADE, 
        related_name="addresses",
        verbose_name="Cliente"
    )
    city = models.ForeignKey(
        City, 
        on_delete=models.PROTECT, 
        verbose_name="Cidade"
    )
    
    zip_code = models.CharField(max_length=10, verbose_name="CEP")
    street = models.CharField(max_length=255, verbose_name="Logradouro (Rua/Av)")
    number = models.CharField(max_length=20, verbose_name="Número")
    complement = models.CharField(max_length=100, blank=True, null=True, verbose_name="Complemento")
    district = models.CharField(max_length=100, verbose_name="Bairro")

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"
        db_table = "clients_addresses"

    def __str__(self):
        return f"{self.street}, {self.number} - {self.city.name}"


class ClientContact(NoteBase):
    """
    Contatos do Cliente (Telefones, Emails, etc).
    """
    client = models.ForeignKey(
        Client, 
        on_delete=models.CASCADE, 
        related_name="contacts",
        verbose_name="Cliente"
    )
    contact_type = models.ForeignKey(
        AuxContactType, 
        on_delete=models.PROTECT, 
        verbose_name="Tipo de Contato"
    )
    
    value = models.CharField(max_length=255, verbose_name="Valor (Tel/Email)")

    class Meta:
        verbose_name = "Contato"
        verbose_name_plural = "Contatos"
        db_table = "clients_contacts"

    def __str__(self):
        return f"{self.client}: {self.value}"
