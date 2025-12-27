/* static/js/vertical_tab.js */

document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.verticalTab');
    const contentItems = document.querySelectorAll('.verticalTab-content-item');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // 1. Remove a classe 'active' de TODAS as abas (sidebar)
            tabs.forEach(t => t.classList.remove('active'));

            // 2. Adiciona a classe 'active' apenas na aba CLICADA
            tab.classList.add('active');

            // 3. Pega o ID do conteúdo alvo
            const contentId = tab.getAttribute('data-content');

            // 4. Esconde todos os conteúdos e mostra o correto
            contentItems.forEach(item => {
                item.classList.remove('active');
                if (item.id === contentId) {
                    item.classList.add('active');
                }
            });
        });
    });
});
