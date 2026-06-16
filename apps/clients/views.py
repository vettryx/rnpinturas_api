"""
==============================================================================
Módulo: Visualizações e Controladores (Views)
Caminho: apps/clients/views.py
==============================================================================

Contém a lógica de apresentação e endpoints da API para o módulo de clientes.
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
from django.db import transaction
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.html import format_html
from orders.models import Order

from .forms import ClientAddressFormSet, ClientContactFormSet, ClientForm
from .models import Client


# 1. HOME
class ClientHomeView(CommonAppHomeView):
    title = "Dashboard de Clientes"
    description = "Visão geral dos clientes"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        clients_base = Client.objects.all()

        # --- KPIs para o Dashboard ---
        total_clients = clients_base.count()
        active_clients = clients_base.filter(idle=False).count()
        inactive_clients = clients_base.filter(idle=True).count()

        context["kpis"] = [
            {
                "label": "Total de Clientes",
                "value": total_clients,
                "extra": "clientes",
                "css_class": "kpi-concluido",
                "icon": "groups",
                "url": reverse_lazy("clients:list"),
            },
            {
                "label": "Clientes Ativos",
                "value": active_clients,
                "extra": "ativos",
                "css_class": "kpi-aprovado",
                "icon": "check_circle",
                "url": reverse_lazy("clients:list") + "?idle=False",

            },
            {
                "label": "Inativos",
                "value": inactive_clients,
                "extra": "inativos",
                "css_class": "kpi-reprovado",
                "icon": "cancel",
                "url": reverse_lazy("clients:list") + "?idle=True",
            },
        ]

        # --- Ações Rápidas ---
        context["actions_list"] = [
            {
                "label": "Novo Cliente",
                "url": reverse_lazy("clients:new"),
                "class": "btn-new btn-transparent",
            },
            {
                "label": "Gerenciar Lista",
                "url": reverse_lazy("clients:list"),
                "class": "btn-list btn-transparent",
            },
        ]

        # --- Tabela Dinâmica (Últimos 10 cadastrados) ---
        context["table_columns"] = [
            "Nome",
            "Documento",
            "Status",
        ]

        context["table_rows"] = [
            {
                "cols": [
                    f'<a href="{reverse_lazy("clients:detail", args=[client.pk])}"><strong>{client.name}</strong></a>',
                    client.cpf_cnpj,
                    f'<span class="badge-{client.status_css_class}">{client.status_label}</span>',
                ]
            }
            for client in clients_base.order_by("-id")[:10]
        ]

        # --- Ranking ---
        context["ranking_title"] = "Top Clientes"
        context["ranking_label"] = "Cliente"
        context["ranking_value"] = "Pedidos"

        context["ranking"] = [
            {
                "label": item["client__name"],
                "value": item["total_pedidos"],
                "url": reverse_lazy("clients:detail", args=[item["client_id"]]),
            }
            for item in (
                Order.objects
                .filter(status__id="6")
                .values("client_id", "client__name")
                .annotate(total_pedidos=Count("id"))
                .order_by("-total_pedidos")[:10]
            )
        ]

        return context


# 2. LISTAGEM
class ClientListView(CommonListView):
    model = Client
    title = "Listagem de Clientes"

    header_buttons = [
        {
            "label": "Dashboard",
            "url": reverse_lazy("clients:home"),
            "class": "btn-dashboard",
        },
        {
            "label": "Novo Cliente",
            "url": reverse_lazy("clients:new"),
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
            "name": "cpf_cnpj",
            "label": "Documento",
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
        {"field": "cpf_cnpj", "label": "Documento"},
        {"field": "idle", "label": "Status"},
    ]

    def get_row_data(self, item):
        detail_url = reverse_lazy("clients:detail", args=[item.pk])

        return [
            item.id,
            format_html('<a href="{}">{}</a>', detail_url, item.name),
            item.cpf_cnpj,
            format_html(
                '<span class="badge-{}">{}</span>',
                item.status_css_class,
                item.status_label
            ),
        ]


# 3. DETALHES
class ClientDetailView(CommonDetailView):
    model = Client
    return_url = reverse_lazy("clients:list")

    def get_object(self, queryset=None):
        return (
            super()
            .get_queryset()
            .prefetch_related("addresses__city", "contacts__contact_type")
            .get(pk=self.kwargs.get("pk"))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = self.object

        # ABAS (Tabs)
        context["tabs"] = [
            {
                "id": "tab-dados",
                "label": "Dados Cadastrais",
                "icon": "person",
                "active": True
            },
            {
                "id": "tab-enderecos",
                "label": f"Endereços ({client.addresses.count()})",
                "icon": "location_on",
            },
            {
                "id": "tab-contatos",
                "label": f"Contatos ({client.contacts.count()})",
                "icon": "contacts",
            },
            {
                "id": "tab-pedidos",
                "label": "Pedidos",
                "icon": "receipt_long"
            },
        ]

        # SEÇÕES (Conteúdo de cada aba)
        context["sections"] = [
            # --- Aba 1: Dados Gerais (Grid Label/Value) ---
            {
                "id": "tab-dados",
                "active": True,
                "title": "Informações Gerais",
                "fields": [
                    {"label": "Nome / Razão Social", "value": client.name},
                    {"label": "Nome Fantasia", "value": client.fantasy_name},
                    {"label": "Tipo", "value": client.get_person_type_display()},
                    {"label": "CPF/CNPJ", "value": client.cpf_cnpj},
                    {"label": "RG/IE", "value": client.rg_ie},
                    {
                        "label": "Status",
                        "value": format_html(
                            '<span class="badge-{}">{}</span>',
                            client.status_css_class,
                            client.status_label,
                        )
                    },
                    {"label": "Observações", "value": client.notes},
                ],
            },
            # Aba 2: Endereços (Tabela)
            {
                "id": "tab-enderecos",
                "title": "Endereços Cadastrados",
                "is_table": True,
                "table_headers": [
                    "Cidade",
                    "Logradouro",
                    "Bairro",
                    "CEP",
                    "Observações",
                ],
                "fields": [
                    {
                        "values": [
                            addr.city,
                            f"{addr.street}, {addr.number}",
                            addr.district,
                            addr.zip_code,
                            addr.notes,
                        ]
                    }
                    for addr in client.addresses.all()
                ],
            },
            # Aba 3: Contatos (Tabela)
            {
                "id": "tab-contatos",
                "title": "Contatos Cadastrados",
                "is_table": True,
                "table_headers": ["Tipo", "Contato", "Observação"],
                "fields": [
                    {"values": [ct.contact_type, ct.value, ct.notes]}
                    for ct in client.contacts.all()
                ],
            },
            # Aba 4: Orçamentos (Implantação Futura)
            {
                "id": "tab-pedidos",
                "title": "Histórico de Orçamentos",
                "custom_html": '<p class="p-detail" style="color: var(--text-secondary);">Funcionalidade de orçamentos em desenvolvimento.</p>',
            },
        ]
        return context


# 4. CRIAÇÃO
class ClientCreateView(CommonCreateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy("clients:list")
    title = "Novo Cliente"
    return_url = reverse_lazy("clients:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Garante que temos o form principal (útil quando ocorre erro de validação e o form volta preenchido)
        # Se 'form' estiver em kwargs, usa ele (com erros); senão, cria um novo.
        main_form = kwargs.get("form")
        if not main_form:
            main_form = self.get_form()

        # Inicializa formsets vazios ou com POST data
        if self.request.POST:
            context["address_formset"] = ClientAddressFormSet(self.request.POST)
            context["contact_formset"] = ClientContactFormSet(self.request.POST)
        else:
            context["address_formset"] = ClientAddressFormSet()
            context["contact_formset"] = ClientContactFormSet()

        # Definição das Abas para o Template de Formulário
        context["tabs"] = [
            {"id": "tab-dados", "label": "Dados Principais", "active": True},
            {"id": "tab-enderecos", "label": "Endereços"},
            {"id": "tab-contatos", "label": "Contatos"},
        ]

        # Configuração das Seções para renderizar os forms
        context["sections"] = [
            {
                "id": "tab-dados",
                "active": True,
                "title": "Dados do Cliente",
                # Passamos o objeto form explicitamente para o template
                "form": main_form,
            },
            {
                "id": "tab-enderecos",
                "title": "Gerenciar Endereços",
                "formset": context["address_formset"],
                "helper_text": "Adicione um ou mais endereços.",
            },
            {
                "id": "tab-contatos",
                "title": "Gerenciar Contatos",
                "formset": context["contact_formset"],
                "helper_text": "Telefones, E-mails, etc.",
            },
        ]

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        address_formset = context["address_formset"]
        contact_formset = context["contact_formset"]

        if form.is_valid() and address_formset.is_valid() and contact_formset.is_valid():
            with transaction.atomic():
                # 1. Salva o cliente (Pai)
                self.object = form.save()

                # 2. Salva Endereços
                address_formset.instance = self.object
                address_formset.save()

                # 3. Salva Contatos
                contact_formset.instance = self.object
                contact_formset.save()

            return redirect(self.success_url)
        else:
            # Se der erro, renderiza tudo de novo com os erros visíveis
            return self.render_to_response(self.get_context_data(form=form))


# 5. EDITAR (Cliente Existente)
class ClientUpdateView(CommonUpdateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy("clients:list")
    title = "Editar Cliente"
    return_url = reverse_lazy("clients:list")

    def get_object(self, queryset=None):
        return (
            super()
            .get_queryset()
            .prefetch_related("addresses__city", "contacts__contact_type")
            .get(pk=self.kwargs.get("pk"))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Garante o form principal (com instância ou erros)
        main_form = kwargs.get("form")
        if not main_form:
            main_form = self.get_form()

        # Inicializa formsets com a instância do objeto para carregar dados do banco
        if self.request.POST:
            context["address_formset"] = ClientAddressFormSet(
                self.request.POST, instance=self.object
            )
            context["contact_formset"] = ClientContactFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context["address_formset"] = ClientAddressFormSet(instance=self.object)
            context["contact_formset"] = ClientContactFormSet(instance=self.object)

        context["tabs"] = [
            {"id": "tab-dados", "label": "Dados Principais", "active": True},
            {"id": "tab-enderecos", "label": "Endereços"},
            {"id": "tab-contatos", "label": "Contatos"},
        ]

        context["sections"] = [
            {
                "id": "tab-dados",
                "active": True,
                "title": "Dados do Cliente",
                "form": main_form,
            },
            {
                "id": "tab-enderecos",
                "title": "Gerenciar Endereços",
                "formset": context["address_formset"],
            },
            {
                "id": "tab-contatos",
                "title": "Gerenciar Contatos",
                "formset": context["contact_formset"],
            },
        ]

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        address_formset = context["address_formset"]
        contact_formset = context["contact_formset"]

        if form.is_valid() and address_formset.is_valid() and contact_formset.is_valid():
            with transaction.atomic():
                self.object = form.save()

                address_formset.instance = self.object
                address_formset.save()

                contact_formset.instance = self.object
                contact_formset.save()

            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


# 6. EXCLUIR
class ClientDeleteView(CommonDeleteView):
    model = Client
    success_url = reverse_lazy("clients:list")
    title = "Excluir Cliente"
