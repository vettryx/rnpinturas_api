"""
==============================================================================
Módulo: Views Principais (Projeto)
Caminho: rnpinturas/views.py
==============================================================================

Gerencia as visualizações globais do projeto que não pertencem a um app específico.
Inclui a renderização do Dashboard principal com métricas consolidadas.
"""

from clients.models import Client
from django.views.generic import TemplateView
from orders.models import Order


class HomeView(TemplateView):
    """
    View para a Página Inicial (Dashboard).
    Consolida indicadores de clientes e pedidos recentes para o resumo inicial.
    """
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        """
        Adiciona métricas de negócio ao contexto do Dashboard.
        """
        context = super().get_context_data(**kwargs)

        # Coleta de métricas para os cards do Dashboard
        context["total_clients"] = Client.objects.count()
        context["total_orders"] = Order.objects.count()

        # Lista dos 5 pedidos mais recentes (ordenação decrescente por ID)
        context["recent_orders"] = Order.objects.order_by("-id")[:5]

        return context
