// static/js/pages/login.js
// Логика для страницы входа/регистрации

document.addEventListener('DOMContentLoaded', function () {
    const authForm = document.getElementById('auth-form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const emailInput = document.getElementById('email');
    const emailGroup = document.getElementById('email-group');
    const consentCheckbox = document.getElementById('consent-checkbox');
    const consentGroup = document.getElementById('consent-group');
    const actionInput = document.getElementById('action-input');
    const submitBtn = document.getElementById('main-submit-btn');
    const toggleLink = document.getElementById('toggle-link');
    const togglePrompt = document.getElementById('toggle-prompt');

    let isLoginMode = true;

    // Фокус на поле при загрузке
    if (usernameInput && !usernameInput.value) {
        usernameInput.focus();
    }

    // Переключение между Входом и Регистрацией
    toggleLink.addEventListener('click', function (e) {
        e.preventDefault();
        isLoginMode = !isLoginMode;

        if (isLoginMode) {
            // Режим Входа
            emailGroup.style.display = 'none';
            emailInput.required = false;
            consentGroup.style.display = 'none';
            consentCheckbox.required = false;
            actionInput.value = 'login';
            submitBtn.textContent = '🔐 Войти';
            togglePrompt.textContent = 'Ещё не ведете летопись?';
            toggleLink.textContent = 'Зарегистрироваться';
        } else {
            // Режим Регистрации
            emailGroup.style.display = 'block';
            emailInput.required = true;
            consentGroup.style.display = 'block';
            consentCheckbox.required = true;
            actionInput.value = 'register';
            submitBtn.textContent = '📜 Зарегистрироваться';
            togglePrompt.textContent = 'Уже есть аккаунт?';
            toggleLink.textContent = 'Войти';
        }
    });

    // Валидация перед отправкой
    authForm.addEventListener('submit', function (e) {
        const username = usernameInput.value.trim();
        const password = passwordInput.value;

        if (username.length < 3) {
            e.preventDefault();
            alert('Логин должен содержать минимум 3 символа');
            usernameInput.focus();
            return;
        }

        if (password.length < 4) {
            e.preventDefault();
            alert('Пароль должен содержать минимум 4 символа');
            passwordInput.focus();
            return;
        }

        if (!isLoginMode) {
            if (!emailInput.value.includes('@')) {
                e.preventDefault();
                alert('Пожалуйста, введите корректный адрес электронной почты');
                emailInput.focus();
                return;
            }

            if (!consentCheckbox.checked) {
                e.preventDefault();
                alert('Для регистрации необходимо дать согласие на обработку персональных данных');
                consentCheckbox.focus();
                return;
            }
        }
    });
});