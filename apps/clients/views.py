# apps/clients/views.py

from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
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

# 3. DETALHES (Onde você verá os Orçamentos futuramente)
class ClientDetailView(CommonDetailView):
    model = Client
    template_name = 'clients/client_detail.html' # Usa o apps_detail.html internamente
    return_url = reverse_lazy('clients:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = self.object

        # ABAS (Tabs)
        context['tabs'] = [
            {'id': 'tab-dados', 'label': 'Dados Cadastrais', 'active': True},
            {'id': 'tab-enderecos', 'label': f'Endereços ({client.addresses.count()})'},
            {'id': 'tab-contatos', 'label': f'Contatos ({client.contacts.count()})'},
            {'id': 'tab-orcamentos', 'label': 'Orçamentos (Futuro)'}, # <--- Espaço reservado
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

# 4. CRIAR, EDITAR, EXCLUIR
class ClientCreateView(CommonCreateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:list')
    title = "Novo Cliente"
    return_url = reverse_lazy('clients:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['address_formset'] = ClientAddressFormSet(self.request.POST)
            context['contact_formset'] = ClientContactFormSet(self.request.POST)
        else:
            context['address_formset'] = ClientAddressFormSet()
            context['contact_formset'] = ClientContactFormSet()
        
        # Define sections para o form (igual ao anterior)
        # ... (código das sections igual ao anterior, omiti para poupar espaço)
        return context
    
    # ... form_valid igual ao anterior ...

class ClientUpdateView(ClientCreateView, CommonUpdateView):
    title = "Editar Cliente"
    return_url = reverse_lazy('clients:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['address_formset'] = ClientAddressFormSet(self.request.POST, instance=self.object)
            context['contact_formset'] = ClientContactFormSet(self.request.POST, instance=self.object)
        else:
            context['address_formset'] = ClientAddressFormSet(instance=self.object)
            context['contact_formset'] = ClientContactFormSet(instance=self.object)
        return context

class ClientDeleteView(CommonDeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:list')