"""
==============================================================================
Módulo: Visualizações e Controladores (Views)
Caminho: apps/rooms/views.py
==============================================================================

Contém a lógica de apresentação e endpoints da API para o módulo de cômodos.
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
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.html import format_html

from .forms import RoomForm, RoomPartForm
from .models import Room, RoomPart


# ===== CÔMODOS =====
# 1. HOME
class RoomHomeView(CommonAppHomeView):
    title = "Dashboard de Estruturas"
    description = "Visão geral dos Cômodos e suas Partes (Superfícies)"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        rooms_base = Room.objects.all()
        parts_base = RoomPart.objects.all()

        # --- KPIs para o Dashboard ---
        # Cômodos
        total_rooms = rooms_base.count()
        active_rooms = rooms_base.filter(idle=False).count()
        inactive_rooms = rooms_base.filter(idle=True).count()

        # Partes (Superfícies)
        total_parts = parts_base.count()
        active_parts = parts_base.filter(idle=False).count()
        inactive_parts = parts_base.filter(idle=True).count()

        context["kpis"] = [
            {
                "label": "Total de Cômodos",
                "value": total_rooms,
                "extra": "cômodos",
                "css_class": "kpi-concluido",
                "icon": "other_houses",
                "url": reverse_lazy("rooms:room_list"),
            },
            {
                "label": "Total de Partes (Superfícies)",
                "value": total_parts,
                "extra": "cômodos",
                "css_class": "kpi-concluido",
                "icon": "room_preferences",
                "url": reverse_lazy("rooms:roompart_list"),
            },
            {
                "label": "Cômodos Ativos",
                "value": active_rooms,
                "extra": "ativos",
                "css_class": "kpi-aprovado",
                "icon": "check_circle",
                "url": reverse_lazy("rooms:room_list") + "?idle=False",
            },
            {
                "label": "Partes (Superfícies) Ativas",
                "value": active_parts,
                "extra": "ativas",
                "css_class": "kpi-aprovado",
                "icon": "check_circle",
                "url": reverse_lazy("rooms:roompart_list") + "?idle=False",
            },
            {
                "label": "Cômodos Inativos",
                "value": inactive_rooms,
                "extra": "inativos",
                "css_class": "kpi-reprovado",
                "icon": "cancel",
                "url": reverse_lazy("rooms:room_list") + "?idle=True",
            },
            {
                "label": "Partes (Superfícies) Inativas",
                "value": inactive_parts,
                "extra": "inativas",
                "css_class": "kpi-reprovado",
                "icon": "cancel",
                "url": reverse_lazy("rooms:roompart_list") + "?idle=True",
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

        # --- Tabela Dinâmica (Últimos 10 cadastrados) ---
        context["table_columns"] = [
            "Nome",
            "Tipo",
            "Status",
        ]

        items = []

        # CÔMODOS
        items += [
            {
                "id": room.id,
                "name": room.name,
                "type": "Cômodo",
                "status_label": room.status_label,
                "status_class": room.status_css_class,
                "url": reverse_lazy("rooms:room_detail", args=[room.pk]),
            }
            for room in Room.objects.all()
        ]

        # PARTES
        items += [
            {
                "id": part.id,
                "name": part.name,
                "type": "Parte",
                "status_label": part.status_label,
                "status_class": part.status_css_class,
                "url": reverse_lazy("rooms:roompart_detail", args=[part.pk]),
            }
            for part in RoomPart.objects.all()
        ]

        items = sorted(items, key=lambda x: x["id"], reverse=True)[:10]

        context["table_rows"] = [
            {
                "cols": [
                    f'<a href="{item["url"]}"><strong>{item["name"]}</strong></a>',
                    item["type"],
                    f'<span class="badge-{item["status_class"]}">{item["status_label"]}</span>',
                ]
            }
            for item in items
        ]

        return context


# 2. LiSTAGEM
class RoomListView(CommonListView):
    model = Room
    title = "Listagem de Cômodos"

    header_buttons = [
        {
            "label": "Dashboard",
            "url": reverse_lazy("rooms:home"),
            "class": "btn-dashboard",
        },
        {
            "label": "Gerenciar Partes (Superfícies)",
            "url": reverse_lazy("rooms:roompart_list"),
            "class": "btn-list",
        },
        {
            "label": "Novo Cômodo",
            "url": reverse_lazy("rooms:room_new"),
            "class": "btn-new",
        },
    ]

    search_config = [
        {
            "name": "name",
            "label": "Nome do Cômodo",
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
        {"field": "idle", "label": "Status"},
        {"field": "notes", "label": "Observações"},
    ]

    def get_row_data(self, item):
        detail_url = reverse_lazy("rooms:room_detail", args=[item.pk])

        return [
            item.id,
            format_html('<a href="{}">{}</a>', detail_url, item.name),
            format_html(
                '<span class="badge-{}">{}</span>',
                item.status_css_class,
                item.status_label
            ),
            item.notes,
        ]


# 3. DETALHES
class RoomDetailView(CommonDetailView):
    model = Room
    return_url = reverse_lazy("rooms:room_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = self.object

        # BOTOES PERSONALIZADOS (URLs diferentes do padrão definido)
        context["buttons"] = [
            {
                "class": "btn-edit",
                "url": reverse_lazy("rooms:room_edit", args=[room.pk]),
                "title": "Editar",
                "text": "Editar",
            },
            {
                "class": "btn-delete",
                "url": reverse_lazy("rooms:room_delete", args=[room.pk]),
                "title": "Excluir",
                "text": "Excluir",
            },
            {
                "class": "btn-return",
                "url": self.return_url,
                "title": "Voltar",
                "text": "Voltar",
            },
        ]

    # ABAS (Tabs)
        context["tabs"] = [
            {
                "id": "tab-dados",
                "label": "Dados do Cômodo",
                "icon": "other_houses",
                "active": True
            },
        ]

        # SEÇÕES (Conteúdo de cada aba)
        context["sections"] = [
            {
                "id": "tab-dados",
                "active": True,
                "label": "Informações Gerais",
                "fields": [
                    {"label": "Nome do Cômodo", "value": room.name},
                    {
                        "label": "Status",
                        "value": format_html(
                            '<span class="badge-{}">{}</span>',
                            room.status_css_class,
                            room.status_label,
                        )
                    },
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
            "label": "Dashboard",
            "url": reverse_lazy("rooms:home"),
            "class": "btn-dashboard",
        },
        {
            "label": "Nova Parte (Superfície)",
            "url": reverse_lazy("rooms:roompart_new"),
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
        {"field": "idle", "label": "Status"},
        {"field": "notes", "label": "Observações"},
    ]

    def get_row_data(self, item):
        detail_url = reverse_lazy("rooms:roompart_detail", args=[item.pk])

        return [
            item.id,
            format_html('<a href="{}">{}</a>', detail_url, item.name),
            format_html(
                '<span class="badge-{}">{}</span>',
                item.status_css_class,
                item.status_label
            ),
            item.notes,
        ]


# 2. DETALHES
class RoomPartDetailView(CommonDetailView):
    model = RoomPart
    return_url = reverse_lazy("rooms:roompart_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        part = self.object

        # BOTOES PERSONALIZADOS (URLs diferentes do padrão definido)
        context["buttons"] = [
            {
                "class": "btn-edit",
                "url": reverse_lazy("rooms:roompart_edit", args=[part.pk]),
                "title": "Editar",
                "text": "Editar",
            },
            {
                "class": "btn-delete",
                "url": reverse_lazy("rooms:roompart_delete", args=[part.pk]),
                "title": "Excluir",
                "text": "Excluir",
            },
            {
                "class": "btn-return",
                "url": self.return_url,
                "title": "Voltar",
                "text": "Voltar",
            },

        ]

        # ABAS (Tabs)
        context["tabs"] = [
            {
                "id": "tab-dados",
                "label": "Dados da Parte do Cômodo",
                "icon": "room_preferences",
                "active": True
            },
        ]

        # SEÇÕES (Conteúdo de cada aba)
        context["sections"] = [
            {
                "id": "tab-dados",
                "active": True,
                "label": "Informações Gerais",
                "fields": [
                    {"label": "Nome da Parte", "value": part.name},
                    {
                        "label": "Status",
                        "value": format_html(
                            '<span class="badge-{}">{}</span>',
                            part.status_css_class,
                            part.status_label,
                        )
                    },
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
