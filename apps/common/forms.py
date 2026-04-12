"""
==============================================================================
Módulo: Formulários Comuns (Forms)
Caminho: apps/common/forms.py
==============================================================================

Moldes de formulários genéricos para serem herdados por outros apps,
garantindo padronização visual e de comportamento.
"""

from django import forms


class NoteBaseForm(forms.ModelForm):
    """Molde genérico para formulários que possuem apenas Observações."""
    notes = forms.CharField(
        label="Observações",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "apps-form-input",
                "placeholder": "Observações gerais...",
                "rows": 3,
            }
        ),
    )


class IdleBaseForm(NoteBaseForm):
    """Molde genérico para formulários que possuem Observações e Status Inativo."""

    SIM_NAO = [
        (False, "Não"),
        (True, "Sim"),
    ]

    idle = forms.TypedChoiceField(
        label="Inativo?",
        choices=SIM_NAO,
        coerce=lambda x: x == "True" or x is True,
        widget=forms.Select(
            attrs={
                "class": "apps-form-input select2",
            }
        ),
    )
