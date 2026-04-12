"""
==============================================================================
Módulo: Visualizações e Controladores (Views)
Caminho: apps/services/views.py
==============================================================================

Contém a lógica de apresentação e endpoints da API para o módulo de serviços.
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

from .forms import ServiceForm
from .models import Service


# 1. HOME
class ServiceHomeView(CommonTemplateView):
    template_name = "includes/apps_home.html"
    title = "Dashboard de Serviços"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # --- KPIs para o Dashboard ---
        total_services = Service.objects.count()
        active_services = Service.objects.filter(idle=False).count()
        inactive_services = Service.objects.filter(idle=True).count()

        context["kpis"] = [
            {
                "label": "Total de Serviços",
                "value": total_services,
                "style": "",  # Padrão azul
                "footer": "Base completa",
            },
            {
                "label": "Serviços Ativos",
                "value": active_services,
                "style": "success",  # Borda verde
                "footer": "Em operação",
            },
            {
                "label": "Serviços Inativos",
                "value": inactive_services,
                "style": "alert",
                "footer": "Arquivados",
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

        # --- Itens Recentes (Últimos 5 Criados) ---
        last_services = Service.objects.order_by("-id")[:5]

        context["recent_items"] = []
        for service in last_services:
            context["recent_items"].append(
                {
                "label": service.name,
                "url": reverse_lazy("services:detail", args=[service.pk]),
                "meta": "Inativo" if service.idle else "Ativo",
                }
            )

        return context


# 2. LISTAGEM
class ServiceListView(CommonListView):
    model = Service
    title = "Lista de Serviços"

    header_buttons = [
        {
            "label": "Novo Serviço",
            "url": reverse_lazy("services:new"),
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
        {"field": "notes", "label": "Observações"},
        {"field": "idle", "label": "Inativo?"},
    ]

    def get_row_data(self, item):
        detail_url = reverse_lazy("services:detail", args=[item.pk])
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
class ServiceDetailView(CommonDetailView):
    model = Service
    return_url = reverse_lazy("services:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = self.object

        if service.default_price:
            price_str = f"R$ {service.default_price:,.2f}"
            price = price_str.replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            price = "R$ 0,00"

        # ABAS (Tabs)
        context["tabs"] = [
            {
                "id": "tab-dados",
                "label": "Dados do Serviço",
                "icon": "fas fa-box",
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
                    {"label": "Preço Sugerido", "value": price},
                    {"label": "Status", "value": "Inativo" if service.idle else "Ativo"},
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
