# apps/common/models.py

import re
import unicodedata

from django.db import models


class NoteBase(models.Model):
    """
    Nível 1: Apenas Observações.
    """
    notes = models.TextField(blank=True, null=True, verbose_name="Observações")

    class Meta:
        abstract = True


class IdleBase(NoteBase):
    """
    Nível 2: Observações + Inativo (Idle).
    """
    SIM_NAO = [
        (False, 'Não'),
        (True, 'Sim'),
    ]

    idle = models.BooleanField(
        default=False,
        verbose_name="Inativo?",
        choices=SIM_NAO
    )

    class Meta:
        abstract = True


class AuxContactType(IdleBase):
    """
    Tipos de contato (Ex: E-mail, WhatsApp, Telefone).
    Tabela: aux_contact_type
    """
    name = models.CharField(max_length=255, unique=True, verbose_name="Nome")

    class Meta:
        verbose_name = "Tipo de Contato"
        verbose_name_plural = "Tipos de Contato"
        db_table = "aux_contact_type"

    def __str__(self):
        return self.name


class AuxStatus(IdleBase):
    """
    Status de orçamentos/pedidos (Ex: Pendente, Aprovado, Cancelado).
    Tabela: aux_status
    """
    name = models.CharField(max_length=255, unique=True, verbose_name="Nome")

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Status Auxiliares"
        db_table = "aux_status"

    def __str__(self):
        return self.name


class AuxUnitMeasure(IdleBase):
    """
    Unidades de medida (Ex: m², un, kg, l).
    Tabela: aux_unit_measure
    """
    code = models.CharField(max_length=50, unique=True, verbose_name="Código (Sigla)")
    name = models.CharField(max_length=255, verbose_name="Nome")

    class Meta:
        verbose_name = "Unidade de Medida"
        verbose_name_plural = "Unidades de Medida"
        db_table = "aux_unit_measure"

    def __str__(self):
        return f"{self.name} ({self.code})"


class AddressBase(models.Model):
    """
    Molde Abstrato para Endereços.
    Contém os campos e a lógica de limpeza (Upper/Strip).
    NÃO cria tabela no banco (abstract = True).
    """
    city = models.ForeignKey(
        'cities.City',
        on_delete=models.PROTECT,
        verbose_name="Cidade"
    )
    zip_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="CEP"
    )
    street = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Logradouro (Rua/Av)"
    )
    number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Número"
    )
    complement = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Complemento"
    )
    district = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Bairro"
    )

    class Meta:
        abstract = True

    def __str__(self):
        # Se tiver rua, mostra rua. Senão, mostra só a cidade/bairro.
        local = self.city.name
        if self.district:
            local = f"{self.district} - {local}"

        if self.street:
            numero = self.number if self.number else "S/N"
            return f"{self.street}, {numero} - {local}"

        return local

    def save(self, *args, **kwargs):
        # 1. Limpeza do CEP (Apenas Números)
        if self.zip_code:
            self.zip_code = re.sub(r'[^0-9]', '', self.zip_code)

        # 2. Função auxiliar interna para limpar textos
        def clean_text(text):
            if not text:
                return None
            normalized = unicodedata.normalize('NFKD', text)
            clean = normalized.encode('ASCII', 'ignore').decode('utf-8')
            return clean.strip().upper()

        # Aplica padronização (agora suportando campos vazios)
        self.street = clean_text(self.street)
        self.district = clean_text(self.district)
        self.complement = clean_text(self.complement)
        self.number = clean_text(self.number)

        super().save(*args, **kwargs)


class ContactBase(models.Model):
    """
    Molde Abstrato para Contatos.
    Contém a lógica complexa de formatação de telefone.
    """
    contact_type = models.ForeignKey(
        AuxContactType,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Contato"
    )
    value = models.CharField(
        max_length=255,
        verbose_name="Valor (Tel/Email)"
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.client}: {self.value}"

    def save(self, *args, **kwargs):
        if self.value:
            self.value = self.value.strip()

            # IDs baseados na tabela aux_contact_type:
            # 1: Tel Residencial, 2: Tel Comercial, 3: Cel Pessoal, 4: Cel Corporativo
            PHONES_BR = [1, 2, 3, 4]
            # 5: Email Pessoal, 6: Email Corporativo
            EMAILS = [5, 6]
            # 7: Telefone Exterior
            PHONE_EXT = [7]

            # Lógica para Emails
            if self.contact_type_id in EMAILS:
                self.value = self.value.lower()

            # Lógica para Telefones Brasil (+55)
            elif self.contact_type_id in PHONES_BR:
                # Remove tudo que não for dígito
                numbers = re.sub(r'[^0-9]', '', self.value)

                # (2 dígitos DDD + 9 dígitos número = 11)
                MAX_LENGTH_WITHOUT_COUNTRY_CODE = 11

                # Se o usuário digitou sem o 55 (ex: 31999999999 - tem 10 ou 11 digitos), adicionamos
                # Se ele já digitou 5531..., mantemos.
                if len(numbers) <= MAX_LENGTH_WITHOUT_COUNTRY_CODE:
                    numbers = '55' + numbers

                self.value = f"+{numbers}"

            # Lógica para Telefone Exterior (+Pais...)
            elif self.contact_type_id in PHONE_EXT:
                # Apenas limpa caracteres não numéricos e garante o + no início
                numbers = re.sub(r'[^0-9]', '', self.value)
                self.value = f"+{numbers}"

        super().save(*args, **kwargs)
