"""
==============================================================================
Módulo: Visualizações e Controladores (Views)
Caminho: apps/orders/views.py
==============================================================================

Contém a lógica de apresentação e endpoints da API para o módulo de orders.
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
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.html import format_html
from weasyprint import HTML

from .forms import OrderForm, OrderMaterialFormSet, OrderServiceFormSet
from .models import Order


# 1. HOME
class OrderHomeView(CommonTemplateView):
    template_name = "includes/apps_home.html"
    title = "Dashboard de Orçamentos"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # --- KPIs para o Dashboard ---
        total_orders = Order.objects.count()

        context["kpis"] = [
            {
                "label": "Total de Pedidos",
                "value": total_orders,
                "style": "",
                "footer": "Base completa",
            },
        ]

        # --- Ações Rápidas ---
        context["actions_list"] = [
            {
                "label": "Novo Pedido",
                "url": reverse_lazy("orders:new"),
                "class": "btn-new btn-transparent",
            },
            {
                "label": "Gerenciar Pedidos",
                "url": reverse_lazy("orders:list"),
                "class": "btn-list btn-transparent",
            },
        ]

        # --- Itens Recentes (Últimos 5 cadastrados) ---
        last_orders = Order.objects.order_by("-id")[:5]

        context["recent_items"] = []
        for order in last_orders:
            context["recent_items"].append(
                {
                    "label": f"Pedido {order.id} - {order.client.name}",
                    "url": reverse_lazy("orders:detail", args=[order.pk]),
                    "meta": f"Status: {order.status}",
                }
            )

        return context


# 2. LISTAGEM
class OrderListView(CommonListView):
    model = Order
    title = "Listagem de Orçamentos"

    header_buttons = [
        {
            "label": "Novo Orçamento",
            "url": reverse_lazy("orders:new"),
            "class": "btn-new"
        }
    ]

    search_config = [
        {"name": "order_code", "label": "Código", "type": "text"},
        {"name": "client__name", "label": "Cliente", "type": "text"},
        {
            "name": "status",
            "label": "Status",
            "type": "select",
            "options": "status_options"
        },
    ]
    table_headers = [
        {"field": "order_code", "label": "Número"},
        {"field": "client", "label": "Cliente"},
        {"field": "issue_date", "label": "Emissão"},
        {"field": "due_date", "label": "Vencimento"},
        {"field": "lead_time", "label": "Prazo (dias)"},
        {"field": "status", "label": "Status"},
    ]

    def get_row_data(self, item):
        detail_url = reverse_lazy("orders:detail", args=[item.pk])

        return [
            item.order_code,
            format_html('<a href="{}">{}</a>', detail_url, item.client.name),
            item.issue_date.strftime("%d/%m/%Y") if item.issue_date else "-",
            item.status.name,
        ]


# 3. DETALHES
class OrderDetailView(CommonDetailView):
    model = Order
    return_url = reverse_lazy("orders:list")

    def get_object(self, queryset=None):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "services__service",
                "services__room",
                "services__room_part",
                "materials__material"
            )
            .get(pk=self.kwargs.get("pk"))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object

        # BOTOES PERSONALIZADOS
        context["buttons"] = [
            {
                "text": "Gerar PDF",
                "url": reverse_lazy("orders:pdf", args=[order.pk]),
                "class": "btn-pdf btn-dark",
                "icon": "fas fa-file-pdf",
            },
            *context.get("buttons", [])
        ]

        # ABAS (Tabs)
        context["tabs"] = [
            {
                "id": "tab-dados",
                "label": "Dados Gerais",
                "icon": "fas fa-file-invoice",
                "active": True,
            },
            {
                "id": "tab-servicos",
                "label": f"Serviços ({order.services.count()})",
                "icon": "fas fa-tools",
            },
            {
                "id": "tab-materiais",
                "label": f"Materiais ({order.materials.count()})",
                "icon": "fas fa-paint-roller",
            },
        ]

        # SEÇÕES (Conteúdo de cada aba)
        context["sections"] = [
            {
                "id": "tab-dados",
                "active": True,
                "title": "Informações do Pedido",
                "fields": [
                    {"label": "Cliente", "value": order.client.name},
                    {"label": "Status", "value": order.status.name},
                    {"label": "Emissão", "value": order.issue_date},
                    {"label": "Vencimento", "value": order.due_date},
                    {"label": "Prazo", "value": f"{order.lead_time} dias"},
                    {"label": "Observações", "value": order.notes},
                ],
            },
            {
                "id": "tab-servicos",
                "title": "Serviços do Pedido",
                "is_table": True,
                "table_headers": [
                    "Serviço",
                    "Ambiente",
                    "Quantidade",
                    "Preço (R$)",
                    "Desconto",
                    "Total",
                    "Observações",
                ],
                "fields": [
                    {
                        "values": [
                            service.service.name,
                            f"{service.room.name} ({service.room_part.name})"
                            if service.room_part
                            else service.room.name,
                            service.quantity,
                            service.price,
                            service.discount,
                            service.total_price,
                            service.notes,
                        ]
                    }
                    for service in order.services.all()
                ],
            },
            {
                "id": "tab-materiais",
                "title": "Materiais que serão utilizados na Prestação dos Serviços",
                "is_table": True,
                "table_headers": [
                    "Material",
                    "Quantidade",
                    "Preço (R$)",
                    "Desconto",
                    "Total",
                    "Observações",
                ],
                "fields": [
                    {
                        "values": [
                            material.material.name,
                            f"{material.quantity} {material.unit_measure.name}",
                            material.price,
                            material.discount,
                            material.total_price,
                            material.notes,
                        ]
                    }
                    for material in order.materials.all()
                ],
            },
        ]
        return context


# 4. CRIAÇÃO
class OrderCreateView(CommonCreateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy("orders:list")
    title = "Novo Pedido"
    return_url = reverse_lazy("orders:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtenção do formulário principal (OrderForm) para renderizar na aba de dados gerais
        main_form = kwargs.get("form")
        if not main_form:
            main_form = self.get_form()

        # Inicialização dos formsets vazios ou com os dados enviados via POST
        if self.request.POST:
            context["service_formset"] = OrderServiceFormSet(self.request.POST)
            context["material_formset"] = OrderMaterialFormSet(self.request.POST)
        else:
            context["service_formset"] = OrderServiceFormSet()
            context["material_formset"] = OrderMaterialFormSet()

        # ABAS (Tabs)
        context["tabs"] = [
            {
                "id": "tab-dados",
                "label": "Dados Principais",
                "active": True
            },
            {
                "id": "tab-servicos",
                "label": "Serviços"
            },
            {
                "id": "tab-materiais",
                "label": "Materiais"
            },
        ]

        # SEÇÕES (Conteúdo de cada aba)
        context["sections"] = [
            {
                "id": "tab-dados",
                "active": True,
                "title": "Dados do Pedido",
                "form": main_form,
            },
            {
                "id": "tab-servicos",
                "title": "Gerenciar Serviços",
                "formset": context["service_formset"],
                "helper_text": "Adicione um ou mais serviços.",
            },
            {
                "id": "tab-materiais",
                "title": "Gerenciar Materiais",
                "formset": context["material_formset"],
                "helper_text": "Adicione um ou mais materiais.",
            },
        ]
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        service_formset = context["service_formset"]
        material_formset = context["material_formset"]

        if form.is_valid() and service_formset.is_valid() and material_formset.is_valid():
            with transaction.atomic():
                # 1. Salvamento do Pedido (Pai)
                self.object = form.save()

                # 2. Salvamento dos Serviços (Filhos)
                service_formset.instance = self.object
                service_formset.save()

                # 3. Salvamento dos Materiais (Filhos)
                material_formset.instance = self.object
                material_formset.save()

            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


# 5. EDIÇÃO
class OrderUpdateView(CommonUpdateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy("orders:list")
    title = "Editar Orçamento"
    return_url = reverse_lazy("orders:list")

    def get_object(self, queryset = None):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "services__service",
                "services__room",
                "services__room_part",
                "materials__material"
            )
            .get(pk=self.kwargs.get("pk"))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtenção do formulário principal (OrderForm) para renderizar na aba de dados gerais
        main_form = kwargs.get("form")
        if not main_form:
            main_form = self.get_form()

        # Inicialização dos formsets com os dados do pedido ou com os dados enviados via POST
        if self.request.POST:
            context["service_formset"] = OrderServiceFormSet(
                self.request.POST, instance=self.object
            )
            context["material_formset"] = OrderMaterialFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context["service_formset"] = OrderServiceFormSet(instance=self.object)
            context["material_formset"] = OrderMaterialFormSet(instance=self.object)


        # ABAS (Tabs)
        context["tabs"] = [
            {
                "id": "tab-dados",
                "label": "Dados Principais",
                "active": True
            },
            {
                "id": "tab-servicos",
                "label": "Serviços"
            },
            {
                "id": "tab-materiais",
                "label": "Materiais"
            },
        ]

        # SEÇÕES (Conteúdo de cada aba)
        context["sections"] = [
            {
                "id": "tab-dados",
                "active": True,
                "title": "Dados do Pedido",
                "form": main_form,
            },
            {
                "id": "tab-servicos",
                "title": "Gerenciar Serviços",
                "formset": context["service_formset"],
                "helper_text": "Adicione um ou mais serviços.",
                "layout": "table",
                "table_headers": ["Serviço", "Ambiente", "Parte", "Qtd", "Preço (R$)", "Desconto", "Observações", "Ações"],
            },
            {
                "id": "tab-materiais",
                "title": "Gerenciar Materiais",
                "formset": context["material_formset"],
                "helper_text": "Adicione um ou mais materiais.",
                "layout": "table",
                "table_headers": ["Material", "Unidade", "Qtd", "Preço (R$)", "Desconto", "Observações", "Ações"],
            },
        ]
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        service_formset = context["service_formset"]
        material_formset = context["material_formset"]

        if form.is_valid() and service_formset.is_valid() and material_formset.is_valid():
            with transaction.atomic():
                # 1. Salva o cliente (Pai)
                self.object = form.save()

                # 2. Salva Endereços
                service_formset.instance = self.object
                service_formset.save()

                # 3. Salva Contatos
                material_formset.instance = self.object
                material_formset.save()

            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


# 6. EXCLUSÃO
class OrderDeleteView(CommonDeleteView):
    model = Order
    success_url = reverse_lazy("orders:list")
    title = "Excluir Pedido"


class OrderPDFView(CommonDetailView):
    model = Order

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        order = self.object

        # Calcular total
        services_total = sum(s.total_price for s in order.services.all())
        materials_total = sum(m.total_price for m in order.materials.all())
        total_amount = services_total + materials_total

        context = {
            "order": order,
            "total_amount": total_amount,
            "services_total": services_total,
            "materials_total": materials_total,
        }

        html_string = render_to_string("orders/order_pdf.html", context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri())

        result = html.write_pdf()

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="Pedido_{order.id}.pdf"'
        response["Content-Transfer-Encoding"] = "binary"
        response.write(result)

        return response
