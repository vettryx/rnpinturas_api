"""
==============================================================================
Módulo: Roteamento (URLs)
Caminho: apps/clients/urls.py
==============================================================================

Define as rotas (endpoints) específicas do módulo de clientes.
Mapeia as URLs para as respectivas views (Listagem, Criação, Edição, etc.).
"""

from django.urls import path

from . import views

app_name = "clients"

urlpatterns = [
    # URL página Principal de Clientes (Dashboard)
    path("clients/", views.ClientHomeView.as_view(), name="home"),
    # URLs de Clientes
    path("client/list/", views.ClientListView.as_view(), name="list"),
    path("client/<int:pk>/", views.ClientDetailView.as_view(), name="detail"),
    path("client/new/", views.ClientCreateView.as_view(), name="new"),
    path("client/<int:pk>/edit/", views.ClientUpdateView.as_view(), name="edit"),
    path("client/<int:pk>/delete/", views.ClientDeleteView.as_view(), name="delete"),
]
