# apps/common/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .utils import buscar_dados_cep

class CommonListView(LoginRequiredMixin, ListView):
    """
    Gera automaticamente: search_fields, headers, rows e page_obj
    para alimentar 'includes/table.html' e 'includes/search_fields.html'
    """
    paginate_by = 20
    title = ""
    new_url = ""
    
    # Configurações que as views filhas definem
    search_config = [] # [{'name': 'q', 'type': 'text', 'label': 'Buscar'}]
    table_headers = [] # [{'field': 'name', 'label': 'Nome'}]

    def get_paginate_by(self, queryset):
        return self.request.GET.get('records_per_page', self.paginate_by)

    def get_ordering(self):
        order_by = self.request.GET.get('order_by')
        descending = self.request.GET.get('descending', 'False')
        if order_by:
            return f"-{order_by}" if descending == 'True' else order_by
        return None

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro automático baseado no search_config
        for config in self.search_config:
            field = config.get('name')
            ftype = config.get('type')
            value = self.request.GET.get(field)

            if value:
                if ftype == 'text':
                    queryset = queryset.filter(**{f"{field}__icontains": value})
                elif ftype == 'select' or ftype == 'boolean':
                    if value == 'True':
                        value = True
                    elif value == 'False':
                        value = False
                    queryset = queryset.filter(**{field: value})
        
        ordering = self.get_ordering()
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset

    def get_row_data(self, item):
        raise NotImplementedError("Implemente get_row_data na view filha")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Monta search_fields
        prepared_search = []
        for config in self.search_config:
            c = config.copy()
            c['value'] = self.request.GET.get(config['name'], '')
            c['id'] = f"search-{config['name']}"
            if 'queryset' in config:
                c['options'] = [(o.pk, str(o)) for o in config['queryset']]
            prepared_search.append(c)

        # Monta o contexto padrão
        context.update({
            'title': self.title,
            'new_url': self.new_url,
            'search_fields': prepared_search,
            'headers': self.table_headers,
            'rows': [self.get_row_data(item) for item in context['page_obj']],
            'query_params': self.request.GET.urlencode()
        })
        return context

class CommonFormMixin:
    """
    Gera automaticamente: sections e buttons
    para alimentar 'includes/apps_form.html'
    """
    title = ""
    return_url = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']
        
        # Gera sections automaticamente se não forem definidas manualmente na view filha
        if 'sections' not in context:
            context['sections'] = [
                {
                    'title': 'Dados do Registro',
                    'fields': [field for field in form]
                }
            ]
        
        # Gera botões padrão
        if 'buttons' not in context:
            context['buttons'] = [
                 {
                    'class': 'btn-return',
                    'url': self.return_url,
                    'title': 'Retornar',
                    'text': 'Retornar',
                },
            ]
        
        context['title'] = self.title
        return context

class CommonCreateView(LoginRequiredMixin, CommonFormMixin, CreateView):
    def form_valid(self, form):
        messages.success(self.request, "Registro criado com sucesso!")
        return super().form_valid(form)

class CommonUpdateView(LoginRequiredMixin, CommonFormMixin, UpdateView):
    def form_valid(self, form):
        messages.success(self.request, "Registro atualizado com sucesso!")
        return super().form_valid(form)

class CommonDeleteView(LoginRequiredMixin, DeleteView):
    def form_valid(self, form):
        messages.success(self.request, "Registro excluído!")
        return super().form_valid(form)

class CommonTemplateView(LoginRequiredMixin, TemplateView):
    """
    Para páginas estáticas ou dashboards (Ex: Home do Cliente)
    """
    title = ""
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context

class CommonDetailView(LoginRequiredMixin, DetailView):
    """
    Gera automaticamente: tabs, sections e buttons
    para alimentar 'includes/apps_detail.html'
    """
    title = ""
    return_url = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object

        # Título da Página
        context['title'] = self.title or str(obj)

        # Botões Padrão (Editar, Excluir, Voltar)
        if 'buttons' not in context:
            app = obj._meta.app_label
            # Tenta gerar URLs padrão: clients:update, clients:delete
            try:
                edit_url = reverse_lazy(f'{app}:edit', args=[obj.pk])
                delete_url = reverse_lazy(f'{app}:delete', args=[obj.pk])
            except Exception:
                edit_url = "#"
                delete_url = "#"

            context['buttons'] = [
                {'class': 'btn-edit', 'url': edit_url, 'title': 'Editar', 'text': 'Editar'},
                {'class': 'btn-delete', 'url': delete_url, 'title': 'Excluir', 'text': 'Excluir'},
                {'class': 'btn-return', 'url': self.return_url, 'title': 'Voltar', 'text': 'Voltar'},
            ]
        
        # Se as seções não forem definidas na view filha, cria uma padrão
        if 'sections' not in context:
            context['sections'] = [
                {
                    'title': 'Dados Principais',
                    'active': True,
                    'fields': [{'label': field.verbose_name, 'value': getattr(obj, field.name)} for field in obj._meta.fields]
                }
            ]
            
        return context


@require_http_methods(["GET"])
def api_busca_cep(request, cep):
    """
    Endpoint API para retornar dados do CEP para o front-end.
    """
    resultado = buscar_dados_cep(cep)
    
    if "erro" in resultado:
        return JsonResponse(resultado, status=400)
        
    return JsonResponse(resultado)
