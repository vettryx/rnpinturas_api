"""
==============================================================================
Módulo: Visualizações e Controladores (Views)
Caminho: apps/materials/views.py
==============================================================================

Contém a lógica de apresentação e endpoints da API para o módulo de materiais.
Herdará as views genéricas do app 'common' para padronização.
"""

from common.views import (
    CommonAppHomeView,
    CommonCreateView,
    CommonDeleteView,
    CommonDetailView,
    CommonListView,
    CommonUpdateView,
)
from django.db.models import Sum
from django.urls import reverse_lazy
from django.utils.html import format_html
from orders.models import OrderMaterial

from .forms import MaterialForm
from .models import Material


# 1. HOME
class MaterialHomeView(CommonAppHomeView):
    title = "Dashboard de Materiais"
    description = "Visão geral dos materiais"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        materials_base = Material.objects.all()

        # --- KPIs para o Dashboard ---
        total_materials = materials_base.count()
        active_materials = materials_base.filter(idle=False).count()
        inactive_materials = materials_base.filter(idle=True).count()

        context["kpis"] = [
            {
                "label": "Total de Materiais",
                "value": total_materials,
                "extra": "materiais",
                "css_class": "kpi-concluido",
                "icon": "inventory_2",
                "url": reverse_lazy("materials:list"),
            },
            {
                "label": "Materiais Ativos",
                "value": active_materials,
                "extra": "ativos",
                "css_class": "kpi-aprovado",
                "icon": "check_circle",
                "url": reverse_lazy("materials:list") + "?idle=False",
            },
            {
                "label": "Materiais Inativos",
                "value": inactive_materials,
                "extra": "inativos",
                "css_class": "kpi-reprovado",
                "icon": "cancel",
                "url": reverse_lazy("materials:list") + "?idle=True",
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

        # --- Tabela Dinâmica (Últimos 10 cadastrados) ---
        context["table_columns"] = [
            "Nome",
            "Status",
        ]

        context["table_rows"] = [
            {
                "cols": [
                    f'<a href="{reverse_lazy("materials:detail", args=[material.pk])}"><strong>{material.name}</strong></a>',
                    f'<span class="badge-{material.status_css_class}">{material.status_label}</span>',
                ]
            }
            for material in materials_base.order_by("-id")[:10]
        ]

        # --- Ranking ---
        context["ranking_title"] = "Top Materiais"
        context["ranking_label"] = "Material"
        context["ranking_value"] = "Quantidade"

        context["ranking"] = [
            {
                "label": item["material__name"],
                "value": item["total_materials"],
                "url": reverse_lazy("materials:detail", args=[item["material_id"]]),
            }
            for item in (
                OrderMaterial.objects
                .filter(order__status__id=6)
                .values("material_id", "material__name")
                .annotate(total_materials=Sum("quantity"))
                .order_by("-total_materials")[:10]
            )
        ]

        return context


# 2. LiSTAGEM
class MaterialListView(CommonListView):
    model = Material
    title = "Listagem de Materiais"

    header_buttons = [
        {
            "label": "Dashboard",
            "url": reverse_lazy("materials:home"),
            "class": "btn-dashboard",
        },
        {
            "label": "Novo Material",
            "url": reverse_lazy("materials:new"),
            "class": "btn-new",
        },
    ]

    search_config = [
        {
            "name": "name",
            "label": "Nome",
            "type": "text"
        },
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
        {"field": "idle", "label": "Status"},
        {"field": "notes", "label": "Observações"},
    ]

    def get_row_data(self, item):
        detail_url = reverse_lazy("materials:detail", args=[item.pk])

        return [
            item.id,
            format_html('<a href="{}">{}</a>', detail_url, item.name),
            item.formatted_price,
            format_html(
                '<span class="badge-{}">{}</span>',
                item.status_css_class,
                item.status_label
            ),
            item.notes,
        ]


# 3. DETALHES
class MaterialDetailView(CommonDetailView):
    model = Material
    return_url = reverse_lazy("materials:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        material = self.object

        # ABAS (Tabs)
        context["tabs"] = [
            {
                "id": "tab-dados",
                "label": "Dados do Material",
                "icon": "inventory_2",
                "active": True
            },
        ]

        # SEÇÕES (Conteúdo de cada aba)
        context["sections"] = [
            {
                "id": "tab-dados",
                "active": True,
                "title": "Informações Gerais",
                "fields": [
                    {"label": "Nome do Material", "value": material.name},
                    {"label": "Preço Sugerido", "value": material.formatted_price},
                    {
                        "label": "Status",
                        "value": format_html(
                            '<span class="badge-{}">{}</span>',
                            material.status_css_class,
                            material.status_label,
                        )
                    },
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
