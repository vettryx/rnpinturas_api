"""
==============================================================================
Módulo: Visualizações e Controladores (Views)
Caminho: apps/orders/views.py
==============================================================================

Contém a lógica de apresentação e endpoints da API para o módulo de orders.
Herdará as views genéricas do app 'common' para padronização.
"""
from datetime import timedelta

from clients.models import Client
from common.models import AuxStatus
from common.views import (
    CommonCloneView,
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
from django.urls import reverse, reverse_lazy
from django.utils import timezone
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
        orders_waiting_payment = Order.objects.filter(status__name="Aguardando Pagamento").count()
        orders_approved = Order.objects.filter(status__name="Aprovado").count()
        orders_cancelled = Order.objects.filter(status__name="Cancelado").count()

        context["kpis"] = [
            {
                "label": "Total de Pedidos",
                "value": total_orders,
                "style": "",
                "footer": "Base completa",
            },
            {
                "label": "Pedidos em Aberto",
                "value": orders_waiting_payment,
                "style": "bg-warning",
                "footer": "Aguardando pagamento",
            },
            {
                "label": "Pedidos Aprovados",
                "value": orders_approved,
                "style": "success",
                "footer": "Aprovados",
            },
            {
                "label": "Pedidos Cancelados",
                "value": orders_cancelled,
                "style": "alert",
                "footer": "Cancelados",
            }
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
        {
            "name": "client",
            "label": "Cliente",
            "type": "select",
            "queryset": Client.objects.all(),
        },
        {
            "name": "status",
            "label": "Status",
            "type": "select",
            "queryset": AuxStatus.objects.all(),
        },
        {
            "name": "start_date",
            "label": "Data Inicial",
            "type": "date_from",
        },
        {
            "name": "end_date",
            "label": "Data Final",
            "type": "date_to",
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
        Sobrescreve o queryset adicionando filtros do dashboard.
        """
        queryset = (
            super()
            .get_queryset()
            .select_related(
                "client",
                "status"
            )
            .prefetch_related(
                "services"
            )
        )
        period = self.request.GET.get("period")
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        today = timezone.now().date()

        if start_date:
            queryset = queryset.filter(
                issue_date__gte=start_date
            )

        if end_date:
            queryset = queryset.filter(
                issue_date__lte=end_date
            )

        if period == "7":
            queryset = queryset.filter(issue_date__gte=today - timedelta(days=7))
        elif period == "30":
            queryset = queryset.filter(issue_date__gte=today - timedelta(days=30))
        elif period == "365":
            queryset = queryset.filter(issue_date__gte=today - timedelta(days=365))
        else:
            # Captura a busca customizada e os inputs do search_config
            if start_date:
                queryset = queryset.filter(issue_date__gte=start_date)
            if end_date:
                queryset = queryset.filter(issue_date__lte=end_date)
        return queryset

    def get_row_data(self, item):
        """
        Retorna os dados da linha.
        """
        detail_url = reverse("orders:detail", args=[item.pk])

        formatted_total = number_format(item.grand_total, decimal_pos=2, force_grouping=True)

        return [
            item.formatted_code,
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

        # Formatação dos valores financeiros (Serviços, Materiais, Descontos e Total)
        fmt_services = f"R$ {number_format(order.gross_services, decimal_pos=2, force_grouping=True)}"
        fmt_materials = f"R$ {number_format(order.gross_materials, decimal_pos=2, force_grouping=True)}"

        if order.total_discounts > 0:
            fmt_discounts = f"- R$ {number_format(order.total_discounts, decimal_pos=2, force_grouping=True)}"
        else:
            fmt_discounts = "R$ 0,00"

        fmt_total = f"R$ {number_format(order.grand_total, decimal_pos=2, force_grouping=True)}"

        # Formatação do título da página (Ex: "2025-0001: Cliente XYZ")
        order_display_code = order.formatted_code if order.order_code else f"#{order.id}"

        # Formatação do código do pedido para exibição (Ex: 20250001 -> 2025-0001)
        context["title"] = f"{order_display_code}: {order.client.name}"

        # Montagem das listas de serviços e materiais para exibição nas abas (com formatação adequada)
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
                "text": "Visualizar PDF",
                "url": reverse("orders:pdf", args=[order.pk]),
                "class": "btn-pdf btn-dark",
                "target": "_blank",
            },
            {
                "text": "Baixar PDF",
                "url": reverse("orders:pdf", args=[order.pk]) + "?download=true",
                "class": "btn-download btn-dark",
                "icon": "download",
            },
            *context.get("buttons", [])
        ]

        # ABAS (Tabs)
        context["tabs"] = [
            {
                "id": "tab-dados",
                "label": "Dados Gerais",
                "icon": "receipt_long",
                "active": True,
            },
            {
                "id": "tab-servicos",
                "label": f"Serviços ({order.services.count()})",
                "icon": "handyman",
            },
            {
                "id": "tab-materiais",
                "label": f"Materiais ({order.materials.count()})",
                "icon": "format_paint",
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
            # ABA 2: SERVIÇOS
            # ==========================================
            {
                "id": "tab-servicos",
                "is_table": True,
                "table_headers": [
                    "Serviço",
                    "Ambiente",
                    "Quantidade",
                    "Preço (R$)",
                    "Desconto",
                    "Total",
                    "Observações"
                ],
                "fields": services_list,
            },

            # ==========================================
            # ABA 3: MATERIAIS
            # ==========================================
            {
                "id": "tab-materiais",
                "is_table": True,
                "table_headers": [
                    "Material",
                    "Quantidade",
                    "Preço (R$)",
                    "Desconto",
                    "Total",
                    "Observações"
                ],
                "fields": materials_list,
            },
        ]
        # RESUMO FINANCEIRO
        context['summary_totals'] = [
            {
                "label": "Serviços",
                "value": fmt_services,
            },
            {
                "label": "Materiais",
                "value": fmt_materials,
            },
            {
                "label": "Descontos",
                "value": fmt_discounts,
                "text_class": "danger" if fmt_discounts.startswith("-") else "",
            },
            {
                "label": "Total Líquido",
                "value": fmt_total,
                "text_class": "primary",
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
                # 1. Salva o Pedido (Pai)
                self.object = form.save()

                # 2. Salva os Serviços (Filhos)
                service_formset.instance = self.object
                service_formset.save()

                # 3. Salva os Materiais (Filhos)
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


# 7. GERAÇÃO DE PDF
class OrderPDFView(CommonDetailView):
    model = Order

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

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        order = self.object

        context = {
            "order": order,

            "services_subtotal": order.gross_services,
            "services_discount": order.discount_services,
            "services_total": order.net_services,

            "materials_subtotal": order.gross_materials,
            "materials_discount": order.discount_materials,
            "materials_total": order.net_materials,

            "total_discount": order.total_discounts,
            "total_amount": order.grand_total,
        }

        # Renderiza o template HTML do PDF com o contexto do pedido
        html_string = render_to_string("orders/order_pdf.html", context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        result = html.write_pdf()

        # Verifica se o parâmetro "download" está presente na URL para forçar o download do PDF
        force_download = request.GET.get("download") == "true"
        disposition = "attachment" if force_download else "inline"

        response = HttpResponse(content_type="application/pdf")

        # Define o nome do arquivo para download (ex: "Pedido_2025-0001.pdf") e a codificação de transferência
        response["Content-Disposition"] = f'{disposition}; filename="Pedido_{order.id}.pdf"'
        response["Content-Transfer-Encoding"] = "binary"
        response.write(result)

        return response

# 8. CLONAGEM
class OrderCloneView(CommonCloneView):
    model = Order
    clone_relations = ["services", "materials"]

    def ajustar_campos_clonados(self, obj):
        # Limpa o código do pedido para que um novo seja gerado pelo save() ou banco
        obj.order_code = None
        return obj
