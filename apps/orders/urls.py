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

app_name = "orders"

urlpatterns = [
    # URL página Principal de Orçamentos (Dashboard)
    path("orders/", views.OrderHomeView.as_view(), name="home"),
    # URLs de Orçamentos
    path("orders/list/", views.OrderListView.as_view(), name="list"),
    path("orders/new/", views.OrderCreateView.as_view(), name="new"),
    path("orders/detail/<int:pk>/", views.OrderDetailView.as_view(), name="detail"),
    path("orders/edit/<int:pk>/", views.OrderUpdateView.as_view(), name="edit"),
    path("orders/delete/<int:pk>/", views.OrderDeleteView.as_view(), name="delete"),
    path("orders/clone/<int:pk>/", views.OrderCloneView.as_view(), name="clone"),
    path("orders/pdf/<int:pk>/", views.OrderPDFView.as_view(), name="pdf"),
]
