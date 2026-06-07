"""
==============================================================================
Módulo: Views Principais (Projeto)
Caminho: rnpinturas/views.py
==============================================================================

Gerencia as visualizações globais do projeto que não pertencem a um app específico.
Inclui a renderização do Dashboard principal com métricas consolidadas.
"""

from datetime import timedelta

from django.apps import apps
from django.db.models import F, Sum
from django.urls import URLPattern, URLResolver, get_resolver
from django.utils import timezone
from django.utils.formats import number_format
from django.views.generic import TemplateView
from orders.models import Order


class HomeView(TemplateView):
    """
    View para a Página Inicial (Dashboard).
    Consolida indicadores financeiros, rankings de atividades
    e orçamentos recentes.
    """

    template_name = "home.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        # =====================================================
        # FILTROS
        # =====================================================

        period = self.request.GET.get(
            "period",
            "30"
        )

        start_date = self.request.GET.get(
            "start_date",
            ""
        )

        end_date = self.request.GET.get(
            "end_date",
            ""
        )

        today = timezone.now().date()

        orders_base = (

            Order.objects

            .select_related(
                "client",
                "status"
            )

            .prefetch_related(
                "services",
                "materials"
            )

        )

        # ==========================================
        # FILTRO POR PERÍODO
        # ==========================================

        if period == "7":

            deadline = today - timedelta(
                days=7
            )

            orders_base = orders_base.filter(
                issue_date__gte=deadline
            )

        elif period == "30":

            deadline = today - timedelta(
                days=30
            )

            orders_base = orders_base.filter(
                issue_date__gte=deadline
            )

        elif period == "365":

            deadline = today - timedelta(
                days=365
            )

            orders_base = orders_base.filter(
                issue_date__gte=deadline
            )

        elif (
            period == "custom"
            and start_date
            and end_date
        ):

            orders_base = orders_base.filter(
                issue_date__range=[
                    start_date,
                    end_date
                ]
            )

        # ==========================================
        # MAPEAMENTO DOS KPIs
        # ==========================================

        status_mapping = [

            {
                "nome": "Aguardando Aprovação",
                "css": "status-pending",
                "icon": "schedule"
            },

            {
                "nome": "Aprovado",
                "css": "status-success",
                "icon": "check_circle"
            },

            {
                "nome": "Em andamento",
                "css": "status-progress",
                "icon": "construction"
            },

            {
                "nome": "Aguardando Pagamento",
                "css": "status-waiting",
                "icon": "payments"
            }

        ]

        kpis = []

        for status in status_mapping:

            queryset_status = orders_base.filter(
                status__name=status["nome"]
            )

            quantidade = queryset_status.count()

            soma = sum(
                pedido.grand_total
                for pedido in queryset_status
            )

            kpis.append({

                "label":
                    status["nome"],

                "qtd":
                    quantidade,

                "soma":
                    f"R$ {number_format(soma, decimal_pos=2, force_grouping=True)}",

                "css_class":
                    status["css"],

                "icon":
                    status["icon"]

            })

        context["kpis"] = kpis

        # ==========================================
        # PEDIDOS RECENTES
        # ==========================================

        context["recent_orders"] = (

            orders_base

            .order_by(
                "-issue_date",
                "-id"
            )[:5]

        )

        # ==========================================
        # TOP SERVIÇOS
        # ==========================================

        context["top_services"] = (

            orders_base

            .exclude(
                services__isnull=True
            )

            .values(
                nome=F(
                    "services__service__name"
                )
            )

            .annotate(
                total_realizado=Sum(
                    "services__quantity"
                )
            )

            .order_by(
                "-total_realizado"
            )[:5]

        )

        # ==========================================
        # TOP MATERIAIS
        # ==========================================

        context["top_materials"] = (

            orders_base

            .exclude(
                materials__isnull=True
            )

            .values(
                nome=F(
                    "materials__material__name"
                )
            )

            .annotate(
                total_solicitado=Sum(
                    "materials__quantity"
                )
            )

            .order_by(
                "-total_solicitado"
            )[:5]

        )

        # ==========================================
        # CONTEXTO PARA TEMPLATE
        # ==========================================

        context["period_atual"] = period

        context["start_date"] = start_date

        context["end_date"] = end_date

        return context


class AppsHubView(TemplateView):
    """
    View autônoma refatorada para baixa complexidade ciclomática.
    """
    template_name = "apps_hub.html"

    # Dicionários de configuração agora são atributos da classe para limpeza
    ACTION_TRANSLATIONS = {'home': 'Dashboard', 'list': 'Lista', 'new': 'Novo Registro'}
    ENTITY_TRANSLATIONS = {
        'room': 'Cômodos', 'roompart': 'Partes de Cômodos', 'order': 'Pedidos',
        'client': 'Clientes', 'material': 'Materiais', 'service': 'Serviços'
    }
    IGNORE_NAMESPACES = ['admin', 'auth', 'contenttypes', 'sessions', 'messages', 'staticfiles', 'two_factor', 'cities']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Módulos do Sistema"

        # Chama a função extraída para processar os módulos (Baixa Complexidade)
        discovered_modules = self._discover_app_modules()

        # Ordena as caixas e envia pro template
        discovered_modules.sort(key=lambda x: x['app_name'])
        context['modules'] = discovered_modules
        return context

    def _discover_app_modules(self):
        """Método isolado que varre as rotas do projeto."""
        modules = []
        resolver = get_resolver()

        for url_pattern in resolver.url_patterns:
            if not isinstance(url_pattern, URLResolver):
                continue

            app_namespace = url_pattern.app_name
            if not app_namespace or app_namespace in self.IGNORE_NAMESPACES:
                continue

            try:
                app_config = apps.get_app_config(app_namespace)
            except LookupError:
                continue

            app_data = self._process_app_patterns(app_namespace, app_config, url_pattern.url_patterns)
            if app_data:
                modules.append(app_data)

        return modules

    def _process_app_patterns(self, namespace, app_config, patterns):
        """Método isolado para processar as rotas de um único app."""
        raw_name = getattr(app_config, 'hub_name', app_config.verbose_name)
        app_name = raw_name.replace("Gestão de ", "").strip()

        module_links = []

        for sub_pattern in patterns:
            if not isinstance(sub_pattern, URLPattern):
                continue

            route_str = str(sub_pattern.pattern)
            url_name = sub_pattern.name

            if url_name and '<' not in route_str:
                link_data = self._build_link_data(namespace, url_name, app_name)
                module_links.append(link_data)

        if not module_links:
            return None

        module_links.sort(key=lambda x: ('Dashboard' not in x['label'], x['label']))

        return {
            'app_name': app_name,
            'icon': getattr(app_config, 'icon', 'fa-cube'),
            'links': module_links
        }

    def _build_link_data(self, namespace, url_name, app_name):
        """Método isolado para montar a URL, o Nome e a Classe CSS do botão."""
        if url_name == 'home':
            return {
                'label': "Dashboard",
                'url': f"{namespace}:{url_name}",
                'css_class': 'btn-home' # Puxa o estilo do seu buttons.css
            }

        if '_' in url_name:
            entidade_raw, acao_raw = url_name.split('_')[0], url_name.split('_')[-1]
        else:
            entidade_raw, acao_raw = namespace, url_name

        acao_pt = self.ACTION_TRANSLATIONS.get(acao_raw, acao_raw.title())
        entidade_pt = self.ENTITY_TRANSLATIONS.get(entidade_raw, app_name)

        # Mapeamento Inteligente das Classes de CSS do seu projeto
        css_class = 'btn-list' if acao_raw == 'list' else 'btn-new' if acao_raw == 'new' else 'btn-transparent'

        return {
            'label': f"{acao_pt} de {entidade_pt}",
            'url': f"{namespace}:{url_name}",
            'css_class': css_class # Envia a classe exata pro HTML
        }
