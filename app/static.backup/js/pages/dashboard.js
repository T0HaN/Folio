// static/js/pages/dashboard.js
// Логика для главной панели управления

import { initModals } from '../utils/modal.js';

document.addEventListener('DOMContentLoaded', () => {
    // Инициализация модальных окон
    initModals();

    // Мобильное меню (сайдбар)
    const menuBtn = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');

    if (menuBtn && sidebar) {
        menuBtn.addEventListener('click', () => {
            sidebar.classList.toggle('mobile-open');
        });

        // Закрытие при клике вне меню на мобильных
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 900) {
                if (!sidebar.contains(e.target) && e.target !== menuBtn) {
                    sidebar.classList.remove('mobile-open');
                }
            }
        });
    }
});