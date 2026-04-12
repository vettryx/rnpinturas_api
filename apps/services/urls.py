"""
==============================================================================
Módulo: Roteamento (URLs)
Caminho: apps/services/urls.py
==============================================================================

Define as rotas (endpoints) específicas do módulo de serviços.
Mapeia as URLs para as respectivas views (Listagem, Criação, Edição, etc.).
"""

from django.urls import path

from . import views

app_name = "services"

urlpatterns = [
    # URL página Principal de Serviços (Dashboard)
    path("services/", views.ServiceHomeView.as_view(), name="home"),
    # URLs de Serviços
    path("service/list/", views.ServiceListView.as_view(), name="list"),
    path("service/<int:pk>/", views.ServiceDetailView.as_view(), name="detail"),
    path("service/new/", views.ServiceCreateView.as_view(), name="new"),
    path("service/<int:pk>/edit/", views.ServiceUpdateView.as_view(), name="edit"),
    path("service/<int:pk>/delete/", views.ServiceDeleteView.as_view(), name="delete"),
]
