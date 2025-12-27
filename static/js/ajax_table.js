/* static/js/ajax_table.js */

document.addEventListener('DOMContentLoaded', function() {
    const listContainer = document.getElementById('list-container');
    const searchForm = document.getElementById('search-form');
    const clearBtn = document.getElementById('btn-clear-search');

    // Função principal que busca os dados e atualiza o DOM
    function fetchResults(url) {
        // Feedback visual de carregamento (Opcional: Adicionar classe de loading)
        listContainer.style.opacity = '0.5';
        listContainer.style.pointerEvents = 'none'; // Previne cliques duplos

        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) throw new Error('Erro na requisição');
            return response.text();
        })
        .then(html => {
            // Atualiza apenas o container de resultados
            listContainer.innerHTML = html;
            
            // Atualiza a URL do navegador sem recarregar (Histórico)
            window.history.pushState({path: url}, '', url);
            
            // Reatribui os eventos aos novos elementos carregados via AJAX
            attachDynamicEvents();
        })
        .catch(error => console.error('Error:', error))
        .finally(() => {
            listContainer.style.opacity = '1';
            listContainer.style.pointerEvents = 'auto';
        });
    }

    // Eventos para elementos que surgem dinamicamente (Paginação, Sort, Seletor)
    function attachDynamicEvents() {
        // 1. Paginação e Ordenação (Links)
        const links = listContainer.querySelectorAll('.pagination-link, .sort-link');
        links.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                fetchResults(this.href);
            });
        });

        // 2. Seletor de "Registros por página"
        const perPageSelect = document.getElementById('records_per_page');
        if (perPageSelect) {
            perPageSelect.addEventListener('change', function() {
                // Busca o form que envolve o select (que tem os hidden inputs dos filtros atuais)
                const form = this.closest('form');
                const url = new URL(form.action, window.location.origin);
                const formData = new FormData(form);
                
                // Converte FormData para QueryString
                const params = new URLSearchParams(formData);
                url.search = params.toString();
                
                fetchResults(url.toString());
            });
        }
    }

    // --- EVENTOS ESTÁTICOS (Sidebar) ---

    // 1. Interceptar o Submit do Formulário de Busca
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const url = new URL(this.action, window.location.origin);
            const formData = new FormData(this);
            url.search = new URLSearchParams(formData).toString();
            
            fetchResults(url.toString());
        });
    }

    // 2. Botão Limpar
    if (clearBtn) {
        clearBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Limpa visualmente os inputs do formulário
            if (searchForm) {
                searchForm.reset();
                // Se houver selects customizados ou lógica extra, resetar aqui
            }

            // Busca a URL limpa (href do botão limpar)
            fetchResults(this.href);
        });
    }

    // Inicializa os eventos na primeira carga da página
    attachDynamicEvents();

    // Suporte ao botão "Voltar" do navegador
    window.addEventListener('popstate', function(event) {
        if (event.state && event.state.path) {
            fetchResults(event.state.path); // Carrega via AJAX
        } else {
            window.location.reload(); // Fallback
        }
    });
});
