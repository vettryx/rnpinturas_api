"""
==============================================================================
Módulo: Visualizações e Controladores (Views)
Caminho: apps/materials/views.py
==============================================================================

Contém a lógica de apresentação e endpoints da API para o módulo de materiais.
Herdará as views genéricas do app 'common' para padronização.
"""

from common.views import (
    CommonCreateView,
    CommonDeleteView,
    CommonDetailView,
    CommonListView,
    CommonTemplateView,
    CommonUpdateView,
)
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.html import format_html

from .forms import MaterialForm
from .models import Material


# 1. HOME
class MaterialHomeView(CommonTemplateView):
    template_name = "includes/apps_home.html"
    title = "Dashboard de Materiais"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # --- KPIs para o Dashboard ---
        total_materials = Material.objects.count()
        active_materials = Material.objects.filter(idle=False).count()
        inactive_materials = Material.objects.filter(idle=True).count()

        context["kpis"] = [
            {
                "label": "Total de Materiais",
                "value": total_materials,
                "style": "",  # Padrão azul
                "footer": "Base completa",
            },
            {
                "label": "Materiais Ativos",
                "value": active_materials,
                "style": "success",  # Borda verde
                "footer": "Em operação",
            },
            {
                "label": "Materiais Inativos",
                "value": inactive_materials,
                "style": "alert",
                "footer": "Arquivados",
            },
        ]

        # --- Ações Rápidas ---
        context["actions_list"] = [
            {
                "label": "Novo Material",
                "url": reverse_lazy("materials:new"),
                "class": "btn-new btn-transparent",
            },
            {
                "label": "Gerenciar Lista",
                "url": reverse_lazy("materials:list"),
                "class": "btn-list btn-transparent",
            },
        ]

        # --- Itens Recentes (Últimos 5 Criados) ---
        last_materials = Material.objects.order_by("-id")[:5]

        context["recent_items"] = []
        for c in last_materials:
            context["recent_items"].append(
                {
                    "name": c.name,
                    "url": reverse_lazy("materials:detail", args=[c.pk]),
                    "meta": f"Código interno: {c.pk}",
                }
            )

        return context


# 2. LiSTAGEM
class MaterialListView(CommonListView):
    model = Material
    title = "Listagem de Materiais"

    header_buttons = [
        {
            "label": "Novo Material",
            "url": reverse_lazy("materials:new"),
            "class": "btn-new",
        },
    ]

    search_config = [
        {"name": "name", "label": "Nome", "type": "text"},
        {
            "name": "idle",
            "label": "Inativo?",
            "type": "select",
            "options": [("True", "Sim"), ("False", "Não")],
        },
    ]

    table_headers = [
        {"field": "id", "label": "ID"},
        {"field": "name", "label": "Nome"},
        {"field": "default_price", "label": "Preço Sugerido"},
        {"field": "idle", "label": "Inativo?"},
    ]

    def get_row_data(self, item):
        detail_url = reverse_lazy("materials:detail", args=[item.pk])
        status = "Sim" if item.idle else "Não"

        if item.default_price:
            price_str = f"R$ {item.default_price:,.2f}"
            price = price_str.replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            price = "R$ 0,00"

        return [
            item.id,
            format_html('<a href="{}">{}</a>', detail_url, item.name),
            price,
            status,
        ]


# 3. DETALHES
class MaterialDetailView(CommonDetailView):
    model = Material
    return_url = reverse_lazy("materials:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        material = self.object

        if material.default_price:
            price_str = f"R$ {material.default_price:,.2f}"
            price = price_str.replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            price = "R$ 0,00"

        # ABAS (Tabs)
        context["tabs"] = [
            {"id": "tab-dados", "label": "Dados do Material", "icon": "fas fa-box", "active": True},
        ]

        # SEÇÕES (Conteúdo de cada aba)
        context["sections"] = [
            {
                "id": "tab-dados",
                "active": True,
                "title": "Informações Gerais",
                "fields": [
                    {"label": "Nome do Material", "value": material.name},
                    {"label": "Preço Sugerido", "value": price},
                    {"label": "Status", "value": "Inativo" if material.idle else "Ativo"},
                    {"label": "Observações", "value": material.notes},
                ],
            },
        ]
        return context


# 4. CRIAÇÃO
class MaterialCreateView(CommonCreateView):
    model = Material
    form_class = MaterialForm
    success_url = reverse_lazy("materials:list")
    title = "Novo Material"
    return_url = reverse_lazy("materials:list")


# 5. EDIÇÃO
class MaterialUpdateView(CommonUpdateView):
    model = Material
    form_class = MaterialForm
    success_url = reverse_lazy("materials:list")
    title = "Editar Material"
    return_url = reverse_lazy("materials:list")


# 6. EXCLUSÃO
class MaterialDeleteView(CommonDeleteView):
    model = Material
    success_url = reverse_lazy("materials:list")
    title = "Excluir Material"
    return_url = reverse_lazy("materials:list")
