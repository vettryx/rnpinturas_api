document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Cria o container do modal no corpo da página se não existir
    if (!document.querySelector('.modal-overlay')) {
        const modalDiv = document.createElement('div');
        modalDiv.className = 'modal-overlay';
        modalDiv.id = 'generic-modal';
        document.body.appendChild(modalDiv);
        
        // Fecha ao clicar fora (no fundo escuro)
        modalDiv.addEventListener('click', (e) => {
            if (e.target === modalDiv) closeModal();
        });
    }

    const modalContainer = document.getElementById('generic-modal');

    // 2. Função para abrir o modal
    function openModal(htmlContent) {
        modalContainer.innerHTML = htmlContent;
        // Pequeno delay para permitir a transição CSS
        setTimeout(() => {
            modalContainer.classList.add('active');
        }, 10);

        // Reatribui evento ao botão cancelar (agora carregado dinamicamente)
        const btnClose = modalContainer.querySelector('.btn-close-modal');
        if (btnClose) {
            btnClose.addEventListener('click', (e) => {
                e.preventDefault();
                closeModal();
            });
        }
    }

    // 3. Função para fechar o modal
    function closeModal() {
        modalContainer.classList.remove('active');
        // Limpa o conteúdo após a animação de saída (300ms)
        setTimeout(() => {
            modalContainer.innerHTML = '';
        }, 300);
    }

    // 4. Intercepta cliques nos botões de exclusão (.btn-delete)
    document.body.addEventListener('click', function(e) {
        // Verifica se o clique foi em um botão .btn-delete ou dentro dele (ícone)
        const btn = e.target.closest('.btn-delete');
        
        if (btn) {
            e.preventDefault(); // Não navega para outra página
            const url = btn.getAttribute('href');

            // Busca o HTML do cartão via AJAX
            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (response.ok) return response.text();
                throw new Error('Erro ao carregar modal');
            })
            .then(html => {
                openModal(html);
            })
            .catch(error => {
                console.error(error);
                // Fallback: se der erro no JS, vai para a página normal
                window.location.href = url;
            });
        }
    });
});