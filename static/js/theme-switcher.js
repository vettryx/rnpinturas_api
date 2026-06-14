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

    // Puxa o span em vez do icone diretamente para facilitar a troca de conteúdo
    const iconElement = themeToggleBtn
        ? themeToggleBtn.querySelector('span')
        : null;

    // 1. Verificar preferência salva ou do sistema
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    function setDarkMode() {
        htmlElement.setAttribute('data-theme', 'dark');
        if (iconElement) {
            iconElement.classList.remove('icon-dark-mode');
            iconElement.classList.add('icon-light-mode');
        }
    }

    function setLightMode() {
        htmlElement.setAttribute('data-theme', 'light');
        if (iconElement) {
            iconElement.classList.remove('icon-light-mode');
            iconElement.classList.add('icon-dark-mode');
        }
    }

    // Inicialização
    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
        setDarkMode();
    } else {
        setLightMode();
    }


    // Clique
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-theme');

            if (currentTheme === 'dark') {
                localStorage.setItem('theme', 'light');
                setLightMode();
            } else {
                localStorage.setItem('theme', 'dark');
                setDarkMode();
            }
        });
    }
});
