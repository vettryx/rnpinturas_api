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
            listContainer.innerHTML = html;
            window.history.pushState({path: url}, '', url);
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
                const form = this.closest('form');
                const url = new URL(form.action, window.location.origin);
                const formData = new FormData(form);
                url.search = new URLSearchParams(formData).toString();
                fetchResults(url.toString());
            });
        }
    }

    // --- EVENTOS ESTÁTICOS (Sidebar) ---

    if (searchForm) {
        let timeout = null;

        // Função central para disparar a busca
        const triggerSearch = () => {
            const url = new URL(searchForm.action, window.location.origin);
            const formData = new FormData(searchForm);
            url.search = new URLSearchParams(formData).toString();
            fetchResults(url.toString());
        };

        // Previne o submit tradicional (caso o usuário dê Enter)
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            triggerSearch();
        });

        // Dispara automaticamente ao alterar selects, checkboxes e datas
        searchForm.addEventListener('change', function(e) {
            if (e.target.type !== 'text' && !e.target.classList.contains('select2')) {
                triggerSearch();
            }
        });

        // Dispara automaticamente ao digitar em campos de texto (com delay de 500ms)
        searchForm.addEventListener('input', function(e) {
            if (e.target.type === 'text') {
                clearTimeout(timeout);
                timeout = setTimeout(triggerSearch, 500);
            }
        });

        // 2. Integração com Select2 (Requer jQuery)
        if (typeof jQuery !== 'undefined') {
            $('.select2').on('change', function() {
                triggerSearch();
            });
        }

        // 3. Botão Limpar ÚNICO
        if (clearBtn) {
            clearBtn.addEventListener('click', function(e) {
                e.preventDefault();
                searchForm.reset();
                triggerSearch();if (typeof jQuery !== 'undefined') {
                    $('.select2').val(null).trigger('change.select2');
                }
                triggerSearch();
            });
        }
    }

    // Inicializa os eventos na primeira carga da página
    attachDynamicEvents();

    window.addEventListener('popstate', function(event) {
        if (event.state && event.state.path) {
            fetchResults(event.state.path);
        } else {
            window.location.reload();
        }
    });
});
