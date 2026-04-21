"""
==============================================================================
Módulo: Views Principais (Projeto)
Caminho: rnpinturas/views.py
==============================================================================

Gerencia as visualizações globais do projeto que não pertencem a um app específico.
Inclui a renderização do Dashboard principal com métricas consolidadas.
"""

from datetime import timedelta

from clients.models import Client
from django.db.models import F, Sum
from django.utils import timezone
from django.utils.formats import number_format
from django.views.generic import TemplateView
from orders.models import Order


class HomeView(TemplateView):
    """
    View para a Página Inicial (Dashboard).
    Consolida indicadores financeiros, rankings de atividades e orçamentos recentes.
    """
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. FILTRO DE PERÍODO (Pega via GET da URL, padrão: 30 dias)
        period = self.request.GET.get('period', '30')
        today = timezone.now().date()

        if period == '7':
            deadline = today - timedelta(days=7)
        elif period == '30':
            deadline = today - timedelta(days=30)
        elif period == '365':
            deadline = today - timedelta(days=365)
        else:
            deadline = None # Todo o período

        # Filtra os pedidos base baseados no período (se houver)
        orders_base = Order.objects.select_related('client', 'status').prefetch_related('services', 'materials')

        if deadline:
            orders_base = orders_base.filter(issue_date__gte=deadline)

        # 2. KPIs INTELIGENTES
        status_mapping = [
            {'nome': 'Aguardando Aprovação', 'css': 'status-pending', 'icon': 'fa-clock'},
            {'nome': 'Aprovado', 'css': 'status-success', 'icon': 'fa-check-circle'},
            {'nome': 'Em andamento', 'css': 'status-progress', 'icon': 'fa-tools'},
            {'nome': 'Aguardando Pagamento', 'css': 'status-waiting', 'icon': 'fa-file-invoice-dollar'},
        ]

        kpis = []


        for st in status_mapping:
            # Filtra pedidos por status
            orders_status = orders_base.filter(status__name=st['nome'])
            quantidade = orders_status.count()

            # Cálculo via Python usando o "Fat Model" (Rápido graças ao prefetch da linha 42)
            soma = sum(p.grand_total for p in orders_status)

            kpis.append({
                'label': st['nome'],
                'qtd': quantidade,
                'soma': f"R$ {number_format(soma, decimal_pos=2, force_grouping=True)}",
                'css_class': st['css'],
                'icon': st['icon']
            })

        context['kpis'] = kpis

        # 3. ÚLTIMOS ORÇAMENTOS (Com código e valor)
        context['recent_orders'] = orders_base.order_by('-issue_date', '-id')[:5]

        # 4. RANKINGS (Serviços e Materiais)
        context['top_services'] = orders_base.exclude(services__isnull=True).values(
            nome=F('services__service__name')
        ).annotate(
            total_realizado=Sum('services__quantity')
        ).order_by('-total_realizado')[:5]

        context['top_materials'] = orders_base.exclude(materials__isnull=True).values(
            nome=F('materials__material__name')
        ).annotate(
            total_solicitado=Sum('materials__quantity')
        ).order_by('-total_solicitado')[:5]

        context['period_atual'] = period

        return context
