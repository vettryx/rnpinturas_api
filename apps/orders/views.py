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
from django.utils.formats import number_format
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
                    "label": f"{order.order_code} - {order.client.name}",
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
        {"field": "issue_date", "label": "Emissão"},
        {"field": "client", "label": "Cliente"},
        {"field": "status", "label": "Status"},
        {"field": "total_services", "label": "Valor Total (R$)"},
        {"field": "notes", "label": "Observações"},
    ]

    def get_queryset(self):
        """
        Sobrescreve o queryset para otimizar as consultas.
        """
        queryset = super().get_queryset()
        return queryset.select_related('client', 'status').prefetch_related('services')

    def get_row_data(self, item):
        """
        Retorna os dados da linha.
        """
        detail_url = reverse_lazy("orders:detail", args=[item.pk])

        # Formatação do código do pedido (Ex: 20250001 -> 2025-0001)
        if item.order_code:
            code_str = str(item.order_code)
            # Pega os 4 primeiros caracteres, coloca o traço, e pega os 4 últimos
            formatted_code = f"{code_str[:4]}-{code_str[-4:]}"
        else:
            # Fallback de segurança caso seja um pedido antigo sem código salvo
            formatted_code = f"{item.id:04d}"

        # Cálculo do valor total via Python (sem onerar o banco com propriedades dinâmicas)
        total_services = sum(s.total_price for s in item.services.all()) if item.services.all() else 0
        formatted_total = number_format(total_services, decimal_pos=2, force_grouping=True)

        return [
            formatted_code,
            item.issue_date.strftime("%d/%m/%Y") if item.issue_date else "-",
            format_html('<a href="{}">{}</a>', detail_url, item.client.name),
            item.status.name,
            f"R$ {formatted_total}",
            item.notes,
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
                "materials__material",
                "materials__unit_measure"
            )
            .get(pk=self.kwargs.get("pk"))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object

        # 1. CÁLCULO FINANCEIRO (Processado em Python para aceitar @property)
        sum_services = sum(s.total_price for s in order.services.all()) if order.services.exists() else 0
        sum_materials = sum(m.total_price for m in order.materials.all()) if order.materials.exists() else 0
        grand_total = sum_services + sum_materials

        # 2. FORMATAÇÃO DE MOEDA (Padrão: R$ 1.000,00)
        fmt_services = f"R$ {number_format(sum_services, decimal_pos=2, force_grouping=True)}"
        fmt_materials = f"R$ {number_format(sum_materials, decimal_pos=2, force_grouping=True)}"
        fmt_total = f"R$ {number_format(grand_total, decimal_pos=2, force_grouping=True)}"

        # 3. FORMATAÇÃO DO CÓDIGO DO PEDIDO (Ex: 2025-0002)
        if order.order_code:
            code_str = str(order.order_code)
            order_display_code = f"{code_str[:4]}-{code_str[-4:]}"
        else:
            order_display_code = f"#{order.id}"

        context["title"] = f"{order_display_code}: {order.client.name}"

        # 4. MONTAGEM DAS LINHAS DAS TABELAS (Dados crus, sem totais internos)
        services_list = [
            {
                "values": [
                    service.service.name,
                    f"{service.room.name} ({service.room_part.name})" if service.room_part else service.room.name,
                    service.quantity,
                    number_format(service.price, decimal_pos=2, force_grouping=True),
                    number_format(service.discount, decimal_pos=2, force_grouping=True) if service.discount else "-",
                    number_format(service.total_price, decimal_pos=2, force_grouping=True),
                    service.notes or "-",
                ]
            }
            for service in order.services.all()
        ]

        materials_list = [
            {
                "values": [
                    material.material.name,
                    f"{material.quantity} {material.unit_measure.name}" if material.unit_measure else material.quantity,
                    number_format(material.price, decimal_pos=2, force_grouping=True),
                    number_format(material.discount, decimal_pos=2, force_grouping=True) if material.discount else "-",
                    number_format(material.total_price, decimal_pos=2, force_grouping=True),
                    material.notes or "-",
                ]
            }
            for material in order.materials.all()
        ]

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
            # ==========================================
            # ABA 1: DADOS GERAIS - INFORMAÇÕES
            # ==========================================
            {
                "id": "tab-dados",
                "active": True,
                "title": "Informações do Pedido",
                "fields": [
                    {"label": "Código do Pedido", "value": order_display_code},
                    {"label": "Cliente", "value": order.client.name},
                    {"label": "Status", "value": order.status.name},
                    {"label": "Emissão", "value": order.issue_date.strftime("%d/%m/%Y") if order.issue_date else "-"},
                    {"label": "Vencimento", "value": order.due_date.strftime("%d/%m/%Y") if order.due_date else "-"},
                    {"label": "Prazo", "value": f"{order.lead_time} dias" if order.lead_time else "-"},
                    {"label": "Observações", "value": order.notes or "-"},
                ],
            },
            # ==========================================
            # ABA 1: DADOS GERAIS - RESUMO FINANCEIRO (SEPARADO)
            # ==========================================
            {
                "id": "tab-dados",
                "active": True,
                "title": "Resumo Financeiro",
                "is_table": False,
                "fields": [
                    {"label": "Total de Serviços", "value": fmt_services, "class": "text-primary font-weight-bold"},
                    {"label": "Total de Materiais", "value": fmt_materials, "class": "text-primary font-weight-bold"},
                    {"label": "VALOR TOTAL DO PEDIDO", "value": fmt_total, "class": "text-success font-weight-bold h5"},
                ],
            },
            # ==========================================
            # ABA 2: SERVIÇOS
            # ==========================================
            {
                "id": "tab-servicos",
                "title": "Serviços do Pedido",
                "is_table": False,
                "fields": [
                    {"label": "VALOR TOTAL DOS SERVIÇOS:", "value": fmt_services, "class": "text-right font-weight-bold h5"}
                ],
            },
            {
                "id": "tab-servicos",
                "is_table": True,
                "table_headers": ["Serviço", "Ambiente", "Quantidade", "Preço (R$)", "Desconto", "Total", "Observações"],
                "fields": services_list,
            },

            # ==========================================
            # ABA 3: MATERIAIS
            # ==========================================
            {
                "id": "tab-materiais",
                "title": "Materiais que serão utilizados na Prestação dos Serviços",
                "is_table": False,
                "fields": [
                    {"label": "VALOR TOTAL DOS MATERIAIS:", "value": fmt_materials, "class": "text-right font-weight-bold h5"}
                ],
            },
            {
                "id": "tab-materiais",
                "is_table": True,
                "table_headers": ["Material", "Quantidade", "Preço (R$)", "Desconto", "Total", "Observações"],
                "fields": materials_list,
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
