# apps/clients/views.py

from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.shortcuts import redirect
from common.views import CommonListView, CommonCreateView, CommonUpdateView, CommonDeleteView, CommonDetailView, CommonTemplateView
from .models import Client
from .forms import ClientForm, ClientAddressFormSet, ClientContactFormSet

# 1. HOME (Dashboard do Cliente)
class ClientHomeView(CommonTemplateView):
    template_name = 'clients/client_home.html'
    title = "Visão Geral de Clientes"

# 2. LISTA
class ClientListView(CommonListView):
    model = Client
    template_name = 'clients/client_list.html'
    title = "Listagem de Clientes"
    new_url = reverse_lazy('clients:new')

    search_config = [
        {'name': 'name', 'label': 'Nome', 'type': 'text'},
        {'name': 'cpf_cnpj', 'label': 'Documento', 'type': 'text'},
        {'name': 'idle', 'label': 'Inativo?', 'type': 'select', 'options': [('True', 'Sim'), ('False', 'Não')]}
    ]

    table_headers = [
        {'field': 'name', 'label': 'Nome'},
        {'field': 'cpf_cnpj', 'label': 'Documento'},
        {'field': 'idle', 'label': 'Status'},
        {'field': 'actions', 'label': 'Ações'},
    ]

    def get_row_data(self, item):
        detail_url = reverse_lazy('clients:detail', args=[item.pk])
        edit_url = reverse_lazy('clients:edit', args=[item.pk])
        delete_url = reverse_lazy('clients:delete', args=[item.pk])

        status = "Sim" if item.idle else "Não"
        
        actions = f"""
            <a href="{detail_url}" class="btn-icon" title="Ver Detalhes"><i class="fas fa-eye"></i></a>
            <a href="{edit_url}" class="btn-icon" title="Editar"><i class="fas fa-edit"></i></a>
            <a href="{delete_url}" class="btn-icon" title="Excluir"><i class="fas fa-trash"></i></a>
        """

        return [
            mark_safe(f'<a href="{detail_url}">{item.name}</a>'),
            item.cpf_cnpj,
            status,
            mark_safe(actions)
        ]

# 3. DETALHES
class ClientDetailView(CommonDetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    return_url = reverse_lazy('clients:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = self.object

        # ABAS (Tabs)
        context['tabs'] = [
            {'id': 'tab-dados', 'label': 'Dados Cadastrais', 'active': True},
            {'id': 'tab-enderecos', 'label': f'Endereços ({client.addresses.count()})'},
            {'id': 'tab-contatos', 'label': f'Contatos ({client.contacts.count()})'},
            {'id': 'tab-orcamentos', 'label': 'Orçamentos (Futuro)'},
        ]

        # SEÇÕES (Conteúdo de cada aba)
        context['sections'] = [
            # Aba 1: Dados
            {
                'id': 'tab-dados',
                'active': True,
                'title': 'Informações Gerais',
                'fields': [
                    {'label': 'Nome / Razão Social', 'value': client.name},
                    {'label': 'Nome Fantasia', 'value': client.fantasy_name},
                    {'label': 'Tipo', 'value': client.get_person_type_display()},
                    {'label': 'CPF/CNPJ', 'value': client.cpf_cnpj},
                    {'label': 'RG/IE', 'value': client.rg_ie},
                    {'label': 'Status', 'value': 'Inativo' if client.idle else 'Ativo'},
                    {'label': 'Observações', 'value': client.notes},
                ]
            },
            # Aba 2: Endereços (Tabela)
            {
                'id': 'tab-enderecos',
                'title': 'Endereços Cadastrados',
                'is_table': True,
                'headers': ['Cidade', 'Logradouro', 'Bairro', 'CEP'],
                'rows': [
                    [addr.city, f"{addr.street}, {addr.number}", addr.district, addr.zip_code]
                    for addr in client.addresses.all()
                ]
            },
            # Aba 3: Contatos (Tabela)
            {
                'id': 'tab-contatos',
                'title': 'Contatos Cadastrados',
                'is_table': True,
                'headers': ['Tipo', 'Valor', 'Obs'],
                'rows': [
                    [ct.contact_type, ct.value, ct.notes]
                    for ct in client.contacts.all()
                ]
            },
            # Aba 4: Orçamentos (Vazio por enquanto)
            {
                'id': 'tab-orcamentos',
                'title': 'Histórico de Orçamentos',
                'content_html': '<p class="text-muted">Nenhum orçamento emitido ainda.</p>'
            }
        ]
        return context

# 4. CRIAR (Novo Cliente)
class ClientCreateView(CommonCreateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:list')
    title = "Novo Cliente"
    return_url = reverse_lazy('clients:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Garante que temos o form principal (útil quando ocorre erro de validação e o form volta preenchido)
        # Se 'form' estiver em kwargs, usa ele (com erros); senão, cria um novo.
        main_form = kwargs.get('form')
        if not main_form:
            main_form = self.get_form()

        # Inicializa formsets vazios ou com POST data
        if self.request.POST:
            context['address_formset'] = ClientAddressFormSet(self.request.POST)
            context['contact_formset'] = ClientContactFormSet(self.request.POST)
        else:
            context['address_formset'] = ClientAddressFormSet()
            context['contact_formset'] = ClientContactFormSet()

        # Definição das Abas para o Template de Formulário
        context['tabs'] = [
            {'id': 'tab-dados', 'label': 'Dados Principais', 'active': True},
            {'id': 'tab-enderecos', 'label': 'Endereços'},
            {'id': 'tab-contatos', 'label': 'Contatos'},
        ]

        # Configuração das Seções para renderizar os forms
        context['sections'] = [
            {
                'id': 'tab-dados',
                'active': True,
                'title': 'Dados do Cliente',
                # Passamos o objeto form explicitamente para o template
                'form': main_form, 
            },
            {
                'id': 'tab-enderecos',
                'title': 'Gerenciar Endereços',
                'formset': context['address_formset'],
                'helper_text': 'Adicione um ou mais endereços.'
            },
            {
                'id': 'tab-contatos',
                'title': 'Gerenciar Contatos',
                'formset': context['contact_formset'],
                'helper_text': 'Telefones, E-mails, etc.'
            }
        ]
        
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        address_formset = context['address_formset']
        contact_formset = context['contact_formset']

        if form.is_valid() and address_formset.is_valid() and contact_formset.is_valid():
            # 1. Salva o cliente (Pai)
            self.object = form.save()
            
            # 2. Salva Endereços
            address_formset.instance = self.object
            address_formset.save()
            
            # 3. Salva Contatos
            contact_formset.instance = self.object
            contact_formset.save()
            
            return redirect(self.success_url)
        else:
            # Se der erro, renderiza tudo de novo com os erros visíveis
            return self.render_to_response(self.get_context_data(form=form))

# 5. EDITAR (Cliente Existente)
class ClientUpdateView(CommonUpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:list')
    title = "Editar Cliente"
    return_url = reverse_lazy('clients:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Garante o form principal (com instância ou erros)
        main_form = kwargs.get('form')
        if not main_form:
            main_form = self.get_form()

        # Inicializa formsets com a instância do objeto para carregar dados do banco
        if self.request.POST:
            context['address_formset'] = ClientAddressFormSet(self.request.POST, instance=self.object)
            context['contact_formset'] = ClientContactFormSet(self.request.POST, instance=self.object)
        else:
            context['address_formset'] = ClientAddressFormSet(instance=self.object)
            context['contact_formset'] = ClientContactFormSet(instance=self.object)

        context['tabs'] = [
            {'id': 'tab-dados', 'label': 'Dados Principais', 'active': True},
            {'id': 'tab-enderecos', 'label': 'Endereços'},
            {'id': 'tab-contatos', 'label': 'Contatos'},
        ]

        context['sections'] = [
            {
                'id': 'tab-dados',
                'active': True,
                'title': 'Dados do Cliente',
                'form': main_form,
            },
            {
                'id': 'tab-enderecos',
                'title': 'Gerenciar Endereços',
                'formset': context['address_formset'],
            },
            {
                'id': 'tab-contatos',
                'title': 'Gerenciar Contatos',
                'formset': context['contact_formset'],
            }
        ]
        
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        address_formset = context['address_formset']
        contact_formset = context['contact_formset']

        if form.is_valid() and address_formset.is_valid() and contact_formset.is_valid():
            self.object = form.save()
            
            address_formset.instance = self.object
            address_formset.save()
            
            contact_formset.instance = self.object
            contact_formset.save()
            
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))

# 6. EXCLUIR
class ClientDeleteView(CommonDeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:list')