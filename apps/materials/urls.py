"""
==============================================================================
Módulo: Roteamento (URLs)
Caminho: apps/materials/urls.py
==============================================================================

Define as rotas (endpoints) específicas do módulo de materiais.
Mapeia as URLs para as respectivas views (Listagem, Criação, Edição, etc.).
"""

from django.urls import path

from . import views

app_name = "materials"

urlpatterns = [
    # URL página Principal de Materiais (Dashboard)
    path("materials/", views.MaterialHomeView.as_view(), name="home"),
    # URLs de Materiais
    path("material/list/", views.MaterialListView.as_view(), name="list"),
    path("material/<int:pk>/", views.MaterialDetailView.as_view(), name="detail"),
    path("material/new/", views.MaterialCreateView.as_view(), name="new"),
    path("material/<int:pk>/edit/", views.MaterialUpdateView.as_view(), name="edit"),
    path("material/<int:pk>/delete/", views.MaterialDeleteView.as_view(), name="delete"),
]
