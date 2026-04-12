"""
==============================================================================
Módulo: Roteamento (URLs)
Caminho: apps/rooms/urls.py
==============================================================================

Define as rotas (endpoints) específicas do módulo de cômodos.
Mapeia as URLs para as respectivas views (Listagem, Criação, Edição, etc.).
"""

from django.urls import path

from . import views

app_name = "rooms"

urlpatterns = [
    # URL página Principal de Cômodos (Dashboard)
    path("rooms/", views.RoomHomeView.as_view(), name="home"),
    # URLs de Cômodos
    path("room/list/", views.RoomListView.as_view(), name="room_list"),
    path("room/<int:pk>/", views.RoomDetailView.as_view(), name="room_detail"),
    path("room/new/", views.RoomCreateView.as_view(), name="room_new"),
    path("room/<int:pk>/edit/", views.RoomUpdateView.as_view(), name="room_edit"),
    path("room/<int:pk>/delete/", views.RoomDeleteView.as_view(), name="room_delete"),

    # URLs das Partes de Cômodos
    path("roompart/list/", views.RoomPartListView.as_view(), name="roompart_list"),
    path("roompart/<int:pk>/", views.RoomPartDetailView.as_view(), name="roompart_detail"),
    path("roompart/new/", views.RoomPartCreateView.as_view(), name="roompart_new"),
    path("roompart/<int:pk>/edit/", views.RoomPartUpdateView.as_view(), name="roompart_edit"),
    path("roompart/<int:pk>/delete/", views.RoomPartDeleteView.as_view(), name="roompart_delete"),
]
