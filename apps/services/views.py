"""
==============================================================================
Módulo: Visualizações e Controladores (Views)
Caminho: apps/services/views.py
==============================================================================

Contém a lógica de apresentação e endpoints da API para o módulo de serviços.
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
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.html import format_html
from orders.models import OrderService

from .forms import ServiceForm
from .models import Service


# 1. HOME
class ServiceHomeView(CommonAppHomeView):
    title = "Dashboard de Serviços"
    description = "Visão geral dos serviços"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        services_base = Service.objects.all()

        # --- KPIs para o Dashboard ---
        total_services = services_base.count()
        active_services = services_base.filter(idle=False).count()
        inactive_services = services_base.filter(idle=True).count()

        context["kpis"] = [
            {
                "label": "Total de Serviços",
                "value": total_services,
                "extra": "serviços",
                "css_class": "kpi-concluido",
                "icon": "build",
                "url": reverse_lazy("services:list"),
            },
            {
                "label": "Serviços Ativos",
                "value": active_services,
                "extra": "ativos",
                "css_class": "kpi-aprovado",
                "icon": "check_circle",
                "url": reverse_lazy("services:list") + "?idle=False",
            },
            {
                "label": "Serviços Inativos",
                "value": inactive_services,
                "extra": "inativos",
                "css_class": "kpi-reprovado",
                "icon": "cancel",
                "url": reverse_lazy("services:list") + "?idle=True",
            },
        ]

        # --- Ações Rápidas ---
        context["actions_list"] = [
            {
                "label": "Novo Serviço",
                "url": reverse_lazy("services:new"),
                "class": "btn-new btn-transparent",
            },
            {
                "label": "Listar Serviços",
                "url": reverse_lazy("services:list"),
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
                    f'<a href="{
                        reverse_lazy("services:detail",
                        args=[service.pk])
                    }"><strong>{service.name}</strong></a>',
                    f'<span class="badge-{service.status_css_class}">{service.status_label}</span>',
                ]
            }
            for service in services_base.order_by("-id")[:10]
        ]

        # --- Ranking ---
        context["ranking_title"] = "Top Serviços"
        context["ranking_label"] = "Serviço"
        context["ranking_value"] = "Quantidade"

        context["ranking"] = [
            {
                "label": item["service__name"],
                "value": item["total_services"],
                "url": reverse_lazy("services:detail", args=[item["service_id"]]),
            }
            for item in (
                OrderService.objects
                .filter(order__status__id=6)
                .values("service_id", "service__name")
                .annotate(total_services=Sum("quantity"))
                .order_by("-total_services")[:10]
            )
        ]

        return context


# 2. LISTAGEM
class ServiceListView(CommonListView):
    model = Service
    title = "Lista de Serviços"

    header_buttons = [
        {
            "label": "Dashboard",
            "url": reverse_lazy("services:home"),
            "class": "btn-dashboard",
        },
        {
            "label": "Novo Serviço",
            "url": reverse_lazy("services:new"),
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
        detail_url = reverse_lazy("services:detail", args=[item.pk])

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
class ServiceDetailView(CommonDetailView):
    model = Service
    return_url = reverse_lazy("services:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = self.object

        # ABAS (Tabs)
        context["tabs"] = [
            {
                "id": "tab-dados",
                "label": "Dados do Serviço",
                "icon": "build",
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
                    {"label": "Nome do Serviço", "value": service.name},
                    {"label": "Preço Sugerido", "value": service.formatted_price},
                    {
                        "label": "Status",
                        "value": format_html(
                            '<span class="badge-{}">{}</span>',
                            service.status_css_class,
                            service.status_label,
                        )
                    },
                    {"label": "Observações", "value": service.notes},
                ],
            },
        ]
        return context


# 4. CRIAÇÃO
class ServiceCreateView(CommonCreateView):
    model = Service
    form_class = ServiceForm
    success_url = reverse_lazy("services:list")
    title = "Novo Serviço"
    return_url = reverse_lazy("services:list")


# 5. EDIÇÃO
class ServiceUpdateView(CommonUpdateView):
    model = Service
    form_class = ServiceForm
    success_url = reverse_lazy("services:list")
    title = "Editar Serviço"
    return_url = reverse_lazy("services:list")


# 6. EXCLUSÃO
class ServiceDeleteView(CommonDeleteView):
    model = Service
    success_url = reverse_lazy("services:list")
    title = "Excluir Serviço"
    return_url = reverse_lazy("services:list")
