/*
==============================================================================
Módulo: Scripts Globais (Tema)
Caminho: static/js/theme-switcher.js
==============================================================================

Gerencia a alternância entre os temas claro e escuro (Dark Mode).
Lê a preferência salva no localStorage ou do sistema operacional, 
aplica o atributo data-theme no HTML global e alterna o ícone do botão.
==============================================================================
*/

document.addEventListener('DOMContentLoaded', () => {
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const htmlElement = document.documentElement;
    // Puxa o span em vez do i
    const iconElement = themeToggleBtn ? themeToggleBtn.querySelector('span') : null;

    // 1. Verificar preferência salva ou do sistema
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
        htmlElement.setAttribute('data-theme', 'dark');
        if(iconElement) iconElement.textContent = 'light_mode';
    }

    // 2. Evento de Clique
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-theme');
            
            if (currentTheme === 'dark') {
                htmlElement.setAttribute('data-theme', 'light');
                localStorage.setItem('theme', 'light');
                if(iconElement) iconElement.textContent = 'dark_mode';
            } else {
                htmlElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                if(iconElement) iconElement.textContent = 'light_mode';
            }
        });
    }
});
