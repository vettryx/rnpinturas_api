# apps/common/views.py

from http import HTTPStatus

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import NoReverseMatch, reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from .utils import buscar_dados_cep


class CommonListView(LoginRequiredMixin, ListView):
    """
    Gera automaticamente: search_fields, headers, rows e page_obj
    para alimentar 'includes/table.html' e 'includes/search_fields.html'
    """

    template_name = "includes/apps_list.html"
    paginate_by = 20
    title = ""
    header_buttons = []

    # Configurações que as views filhas definem
    search_config = []  # [{'name': 'q', 'type': 'text', 'label': 'Buscar'}]
    table_headers = []  # [{'field': 'name', 'label': 'Nome'}]

    def get_paginate_by(self, queryset):
        return self.request.GET.get("records_per_page", self.paginate_by)

    def get_ordering(self):
        order_by = self.request.GET.get("order_by")
        descending = self.request.GET.get("descending", "False")
        if order_by:
            return f"-{order_by}" if descending == "True" else order_by
        return None

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_kwargs = {}

        # Mapeamento de tipos para os sufixos de lookup do Django ORM
        lookup_map = {
            "text": "__icontains",
            "date_from": "__gte",
            "date_to": "__lte",
            "select": "",   # Exact match
            "boolean": "",  # Exact match
            "date": ""      # Exact match
        }

        # Filtro automático baseado no search_config
        for config in self.search_config:
            field = config.get("name")
            ftype = config.get("type")
            value = self.request.GET.get(field)

            if not value:
                continue

            # Conversão estrita para booleanos
            if ftype in ("select", "boolean") and value in ("True", "False"):
                value = value == "True"

            # Constrói o sufixo dinamicamente (ex: nome__icontains ou apenas status)
            lookup = lookup_map.get(ftype, "")
            filter_kwargs[f"{field}{lookup}"] = value

        # Aplica todos os filtros de uma só vez
        if filter_kwargs:
            queryset = queryset.filter(**filter_kwargs)

        ordering = self.get_ordering()
        if ordering:
            queryset = queryset.order_by(ordering)

        return queryset

    def get_row_data(self, item):
        raise NotImplementedError("Implemente get_row_data na view filha")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. PROCESSAMENTO DA BUSCA
        prepared_search = []
        for config in self.search_config:
            c = config.copy()
            c["value"] = self.request.GET.get(config["name"], "")
            c["id"] = f"search-{config['name']}"
            if "queryset" in config:
                formatter = config.get("format_func", str)
                c["options"] = [(o.pk, formatter(o)) for o in config["queryset"]]
            prepared_search.append(c)

        # 2. PROCESSAMENTO DOS BOTÕES DO CABEÇALHO (header_buttons)
        # Se a view filha não definiu botões, tentamos criar um "Novo" padrão se houver new_url definida
        buttons = self.header_buttons.copy()

        # 3. PROCESSAMENTO DOS BOTÕES DE AÇÃO DA BUSCA (search_actions)
        context["search_actions"] = [
            {"type": "submit", "label": "Buscar", "class": "btn-list"},
            {"type": "clear", "label": "Limpar", "class": "btn-clear", "url": self.request.path},
        ]

        # Monta o contexto padrão
        context.update(
            {
                "title": self.title,
                "header_buttons": buttons,
                "search_fields": prepared_search,
                "headers": self.table_headers,
                "rows": [
                    [cell if cell not in [None, ""] else "" for cell in self.get_row_data(item)]
                    for item in context["page_obj"]
                ],
                "query_params": self.request.GET.urlencode(),
            }
        )
        return context

    def render_to_response(self, context, **response_kwargs):
        """
        Se a requisição for AJAX, retorna apenas o partial_list_results.html.
        Caso contrário, retorna o template completo definido na view filha via template_name.
        """
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return self.response_class(
                request=self.request,
                template="includes/partial_list_results.html",
                context=context,
                **response_kwargs,
            )
        return super().render_to_response(context, **response_kwargs)


class CommonFormMixin:
    """
    Gera automaticamente: sections e buttons
    para alimentar 'includes/apps_form.html'
    """

    title = ""
    return_url = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context.get("form")

        # Gera sections automaticamente APENAS se não forem definidas na view filha
        if "sections" not in context and form:
            context["sections"] = [
                {
                    "id": "general",
                    "title": "Dados do Registro",
                    "fields": list(form),
                    "form": form,
                    "active": True,
                }
            ]

        # Garante que, se houver sections mas não tabs, a primeira section seja active
        # para evitar tabs ocultas se o usuario esquecer o flag 'active'
        sections = context.get("sections")
        if sections:
            has_active = any(s.get("active") for s in sections)
            if not has_active:
                sections[0]["active"] = True

        # Gera botões padrão
        if "buttons" not in context:
            context["buttons"] = [
                {
                    "class": "btn-return",
                    "url": self.return_url or "#",
                    "title": "Retornar",
                    "text": "Retornar",
                },
            ]

        context["title"] = self.title
        return context


class CommonCreateView(LoginRequiredMixin, CommonFormMixin, CreateView):
    template_name = "includes/apps_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Registro criado com sucesso!")
        return super().form_valid(form)


class CommonUpdateView(LoginRequiredMixin, CommonFormMixin, UpdateView):
    template_name = "includes/apps_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Registro atualizado com sucesso!")
        return super().form_valid(form)


class CommonDeleteView(LoginRequiredMixin, DeleteView):
    """
    Padroniza a confirmação de exclusão.
    Se 'return_url' não for definido, tenta usar o 'success_url'.
    """

    template_name = "includes/apps_confirm_delete.html"
    title = "Confirmar Exclusão"
    return_url = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object

        # Define URL de cancelamento (Prioridade: return_url > success_url)
        cancel_url = self.return_url or self.success_url

        context["title"] = self.title
        context["cancel_url"] = cancel_url
        context["object_name"] = str(obj)

        # Botões padronizados para o template renderizar
        # Nota: O botão de confirmar é 'submit', o de cancelar é 'link'
        context["buttons"] = [
            {
                "type": "submit",
                "class": "btn-delete-confirm",
                "text": "Sim, excluir permanentemente",
                "icon": "fas fa-trash-alt",
            },
            {"type": "link", "url": cancel_url, "class": "btn-return", "text": "Cancelar operação"},
        ]
        return context

    def render_to_response(self, context, **response_kwargs):
        """
        Se for requisição AJAX (fetch/axios), retorna apenas o partial do cartão.
        """
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return self.response_class(
                request=self.request,
                template="includes/partial_delete_card.html",
                context=context,
                **response_kwargs,
            )
        return super().render_to_response(context, **response_kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Registro excluído com sucesso!")
        return super().form_valid(form)


class CommonTemplateView(LoginRequiredMixin, TemplateView):
    """
    Para páginas estáticas ou dashboards (Ex: Home do Cliente)
    """

    title = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        return context


class CommonDetailView(LoginRequiredMixin, DetailView):
    """
    Gera automaticamente: tabs, sections e buttons
    para alimentar 'includes/apps_detail.html'
    """

    title = ""
    return_url = ""
    template_name = "includes/apps_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object

        # Título da Página
        context["title"] = self.title or str(obj)

        # Botões Padrão (Editar, Excluir, Voltar)
        if "buttons" not in context:
            app = obj._meta.app_label
            buttons = []

            # Verifica se existe a rota de Clonar
            try:
                clone_url = reverse(f"{app}:clone", args=[obj.pk])
                buttons.append({"class": "btn-clone", "url": clone_url, "title": "Clonar", "text": "Clonar"})
            except NoReverseMatch:
                pass
            # Verifica se existe a rota de Editar
            try:
                edit_url = reverse(f"{app}:edit", args=[obj.pk])
                buttons.append({"class": "btn-edit", "url": edit_url, "title": "Editar", "text": "Editar"})
            except NoReverseMatch:
                pass

            # Verifica se existe a rota de Excluir
            try:
                delete_url = reverse(f"{app}:delete", args=[obj.pk])
                buttons.append({"class": "btn-delete", "url": delete_url, "title": "Excluir", "text": "Excluir"})
            except NoReverseMatch:
                pass

            # O botão de voltar é sempre exibido
            buttons.append({
                "class": "btn-return",
                "url": self.return_url,
                "title": "Voltar",
                "text": "Voltar",
            })

            context["buttons"] = buttons

        # Se as seções não forem definidas na view filha, cria uma padrão
        if "sections" not in context:
            context["sections"] = [
                {
                    "title": "Dados Principais",
                    "active": True,
                    "id": "main-data",
                    "fields": [
                        {"label": field.verbose_name, "value": getattr(obj, field.name)}
                        for field in obj._meta.fields
                    ],
                }
            ]

            # Se não houver abas definidas, cria uma aba única para essa seção
            if "tabs" not in context:
                context["tabs"] = [
                    {
                        "id": "main-data",
                        "label": "Geral",
                        "icon": "fas fa-info-circle",
                        "active": True,
                    }
                ]

        return context

class CommonCloneView(LoginRequiredMixin, View):
    """
    View genérica para clonar um registro pai e seus respectivos filhos.
    """
    model = None
    clone_relations = []  # Lista com os related_names dos filhos (ex: ['services', 'materials'])

    def get(self, request, pk):
        objeto_original = get_object_or_404(self.model, pk=pk)

        with transaction.atomic():
            # 1. Guarda as listas de objetos filhos em memória antes de alterar o pai
            dados_relacionados = {}
            for rel in self.clone_relations:
                dados_relacionados[rel] = list(getattr(objeto_original, rel).all())

            # 2. Clona o objeto principal (pai)
            objeto_clonado = objeto_original
            objeto_clonado.pk = None
            objeto_clonado.id = None
            objeto_clonado = self.ajustar_campos_clonados(objeto_clonado)
            objeto_clonado.save()

            # 3. Clona os filhos associando-os ao novo pai dinamicamente
            for rel, filhos in dados_relacionados.items():
                for filho in filhos:
                    filho.pk = None
                    filho.id = None

                    # Descobre o nome do campo ForeignKey no filho que aponta para o pai
                    campo_fk = getattr(objeto_clonado, rel).field.name
                    setattr(filho, campo_fk, objeto_clonado)
                    filho.save()

        messages.success(request, "Registro clonado com sucesso!")
        app = objeto_clonado._meta.app_label
        return redirect(f"{app}:edit", pk=objeto_clonado.pk)

    def ajustar_campos_clonados(self, obj):
        """
        Sobrescreva na view filha caso precise limpar ou alterar
        algum campo específico (como códigos únicos, datas, etc.) antes de salvar.
        """
        return obj

@require_http_methods(["GET"])
@login_required
def api_busca_cep(request, cep):
    """
    Endpoint API para retornar dados do CEP para o front-end.
    """
    resultado = buscar_dados_cep(cep)

    if "erro" in resultado:
        return JsonResponse(resultado, status=HTTPStatus.BAD_REQUEST)

    return JsonResponse(resultado)
