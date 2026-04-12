"""
==============================================================================
Módulo: Visualizações e Controladores (Views)
Caminho: apps/rooms/views.py
==============================================================================

Contém a lógica de apresentação e endpoints da API para o módulo de cômodos.
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

from .forms import RoomForm, RoomPartForm
from .models import Room, RoomPart


# ===== CÔMODOS =====
# 1. HOME
class RoomHomeView(CommonTemplateView):
    template_name = "includes/apps_home.html"
    title = "Dashboard de Estruturas"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # --- KPIs para o Dashboard ---
        total_rooms = Room.objects.count()
        total_parts = RoomPart.objects.count()
        active_rooms = Room.objects.filter(idle=False).count()

        context["kpis"] = [
            {
                "label": "Total de Cômodos",
                "value": total_rooms,
                "style": "",  # Padrão azul
                "footer": "Cadastrados",
            },
            {
                "label": "Total de Partes/Superfícies",
                "value": total_parts,
                "style": "",  # Padrão azul
                "footer": "Cadastradas",
            },
            {
                "label": "Cômodos Ativos",
                "value": active_rooms,
                "style": "success",  # Borda verde
                "footer": "Em operação",
            },
        ]

        # --- Ações Rápidas ---
        context["actions_list"] = [
            {
                "label": "Novo Cômodo",
                "url": reverse_lazy("rooms:room_new"),
                "class": "btn-new btn-transparent",
            },
            {
                "label": "Gerenciar Cômodos",
                "url": reverse_lazy("rooms:room_list"),
                "class": "btn-list btn-transparent",
            },
            {
                "label": "Nova Parte (Superfície)",
                "url": reverse_lazy("rooms:roompart_new"),
                "class": "btn-new btn-transparent",
            },
            {
                "label": "Gerenciar Partes (Superfícies)",
                "url": reverse_lazy("rooms:roompart_list"),
                "class": "btn-list btn-transparent",
            },
        ]

        # --- Itens Recentes (Últimos 5 Criados) ---
        last_rooms = Room.objects.order_by("-id")[:5]

        context["recent_items"] = []
        for room in last_rooms:
            context["recent_items"].append(
                {
                    "label": room.name,
                    "url": reverse_lazy("rooms:room_detail", args=[room.pk]),
                    "meta": "Inativo" if room.idle else "Ativo",
                }
            )

        return context


# 2. LiSTAGEM
class RoomListView(CommonListView):
    model = Room
    title = "Listagem de Cômodos"

    header_buttons = [
        {
            "label": "Novo Cômodo",
            "url": reverse_lazy("rooms:room_new"),
            "class": "btn-new",
        },
        {
            "label": "Gerenciar Partes (Superfícies)",
            "url": reverse_lazy("rooms:roompart_list"),
            "class": "btn-list",
        },
    ]

    search_config = [
        {"name": "name", "label": "Nome do Cômodo", "type": "text"},
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
        {"field": "notes", "label": "Observações"},
        {"field": "idle", "label": "Inativo?"},
    ]

    def get_row_data(self, item):
        detail_url = reverse_lazy("rooms:room_detail", args=[item.pk])
        status = "Sim" if item.idle else "Não"

        return [
            item.id,
            format_html('<a href="{}">{}</a>', detail_url, item.name),
            item.notes,
            status,
        ]


# 3. DETALHES
class RoomDetailView(CommonDetailView):
    model = Room
    return_url = reverse_lazy("rooms:room_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = self.object

    # ABAS (Tabs)
        context["tabs"] = [
            {
                "id": "tab-dados",
                "label": "Dados do Cômodo",
                "icon": "fas fa-box",
                "active": True
            },
        ]

        # SEÇÕES (Conteúdo de cada aba)
        context["sections"] = [
            {
                "id": "tab-dados",
                "active": True,
                "label": "Dados do Cômodo",
                "fields": [
                    {"label": "Nome do Cômodo", "value": room.name},
                    {"label": "Status", "value": "Inativo" if room.idle else "Ativo"},
                    {"label": "Observações", "value": room.notes},
                ],
            },
        ]
        return context


# 4. CRIAÇÃO
class RoomCreateView(CommonCreateView):
    model = Room
    form_class = RoomForm
    success_url = reverse_lazy("rooms:room_list")
    title = "Novo Cômodo"
    return_url = reverse_lazy("rooms:room_list")


# 5. EDIÇÃO
class RoomUpdateView(CommonUpdateView):
    model = Room
    form_class = RoomForm
    success_url = reverse_lazy("rooms:room_list")
    title = "Editar Cômodo"
    return_url = reverse_lazy("rooms:room_list")


# 6. EXCLUSÃO
class RoomDeleteView(CommonDeleteView):
    model = Room
    success_url = reverse_lazy("rooms:room_list")
    title = "Excluir Cômodo"
    return_url = reverse_lazy("rooms:room_list")


# ===== PARTES DE CÔMODOS (SUPERFÍCIES) =====
# 1. LiSTAGEM
class RoomPartListView(CommonListView):
    model = RoomPart
    title = "Listagem de Partes de Cômodos (Superfícies)"

    header_buttons = [
        {
            "label": "Nova Parte (Superfície)",
            "url": reverse_lazy("rooms:roompart_new"),
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
        {"field": "notes", "label": "Observações"},
        {"field": "idle", "label": "Inativo?"},
    ]

    def get_row_data(self, item):
        detail_url = reverse_lazy("rooms:roompart_detail", args=[item.pk])
        status = "Sim" if item.idle else "Não"

        return [
            item.id,
            format_html('<a href="{}">{}</a>', detail_url, item.name),
            item.notes,
            status,
        ]


# 2. DETALHES
class RoomPartDetailView(CommonDetailView):
    model = RoomPart
    return_url = reverse_lazy("rooms:roompart_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        part = self.object

        # ABAS (Tabs)
        context["tabs"] = [
            {
                "id": "tab-dados",
                "label": "Dados da Parte do Cômodo",
                "icon": "fas fa-box",
                "active": True
            },
        ]

        # SEÇÕES (Conteúdo de cada aba)
        context["sections"] = [
            {
                "id": "tab-dados",
                "active": True,
                "label": "Dados da Parte do Cômodo",
                "fields": [
                    {"label": "Nome da Parte", "value": part.name},
                    {"label": "Status", "value": "Inativo" if part.idle else "Ativo"},
                    {"label": "Observações", "value": part.notes},
                ],
            },
        ]
        return context


# 3. CRIAÇÃO
class RoomPartCreateView(CommonCreateView):
    model = RoomPart
    form_class = RoomPartForm
    success_url = reverse_lazy("rooms:roompart_list")
    title = "Nova Parte de Cômodo (Superfície)"
    return_url = reverse_lazy("rooms:roompart_list")


# 4. EDIÇÃO
class RoomPartUpdateView(CommonUpdateView):
    model = RoomPart
    form_class = RoomPartForm
    success_url = reverse_lazy("rooms:roompart_list")
    title = "Editar Parte de Cômodo (Superfície)"
    return_url = reverse_lazy("rooms:roompart_list")


# 5. EXCLUSÃO
class RoomPartDeleteView(CommonDeleteView):
    model = RoomPart
    success_url = reverse_lazy("rooms:roompart_list")
    title = "Excluir Parte de Cômodo (Superfície)"
    return_url = reverse_lazy("rooms:roompart_list")
