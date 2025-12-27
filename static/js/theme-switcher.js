/* static/js/theme-switcher.js */

document.addEventListener('DOMContentLoaded', () => {
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const htmlElement = document.documentElement;
    const iconElement = themeToggleBtn ? themeToggleBtn.querySelector('i') : null;

    // 1. Verificar preferência salva ou do sistema
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
        htmlElement.setAttribute('data-theme', 'dark');
        if(iconElement) iconElement.classList.replace('fa-moon', 'fa-sun');
    }

    // 2. Evento de Clique
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-theme');
            
            if (currentTheme === 'dark') {
                htmlElement.setAttribute('data-theme', 'light');
                localStorage.setItem('theme', 'light');
                if(iconElement) iconElement.classList.replace('fa-sun', 'fa-moon');
            } else {
                htmlElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                if(iconElement) iconElement.classList.replace('fa-moon', 'fa-sun');
            }
        });
    }
});
