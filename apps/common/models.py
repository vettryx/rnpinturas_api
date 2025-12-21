# apps/common/models.py

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
