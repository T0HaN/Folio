// static/js/utils/modal.js
// Модуль для работы с модальными окнами

/**
 * Открывает модальное окно по id.
 * @param {string} id - id модального окна (элемент .modal-overlay)
 */
export function openModal(id) {
    const overlay = document.getElementById(id);
    if (overlay) {
        overlay.classList.add('active');
    }
}

/**
 * Закрывает модальное окно по id.
 * @param {string} id - id модального окна (элемент .modal-overlay)
 */
export function closeModal(id) {
    const overlay = document.getElementById(id);
    if (overlay) {
        overlay.classList.remove('active');
    }
}

/**
 * Инициализирует все модальные окна на странице:
 * - закрытие по клику на крестик (.modal-close);
 * - закрытие по клику на затемнение (вне контента).
 */
export function initModals() {
    // Закрытие при клике на крестик
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const overlay = btn.closest('.modal-overlay');
            if (overlay) {
                overlay.classList.remove('active');
            }
        });
    });

    // Закрытие при клике вне контента
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.classList.remove('active');
            }
        });
    });
}