(function () {
    var overlay = document.querySelector('[data-loading-overlay]');
    var loadingMessage = document.querySelector('[data-loading-message]');
    var confirmModalElement = document.getElementById('appConfirmModal');
    var confirmTitle = confirmModalElement ? confirmModalElement.querySelector('[data-confirm-title]') : null;
    var confirmAction = confirmModalElement ? confirmModalElement.querySelector('[data-confirm-action]') : null;
    var confirmMessage = confirmModalElement ? confirmModalElement.querySelector('[data-confirm-message]') : null;
    var confirmModal = confirmModalElement && window.bootstrap
        ? new bootstrap.Modal(confirmModalElement)
        : null;

    function showLoading(message) {
        if (!overlay) {
            return;
        }
        if (loadingMessage) {
            loadingMessage.textContent = message || 'Working on it...';
        }
        overlay.classList.add('is-visible');
        overlay.setAttribute('aria-hidden', 'false');
    }

    function setButtonLoading(button, label) {
        if (!button || button.dataset.loadingApplied === 'true') {
            return;
        }
        if (button.name) {
            var hiddenSubmitValue = document.createElement('input');
            hiddenSubmitValue.type = 'hidden';
            hiddenSubmitValue.name = button.name;
            hiddenSubmitValue.value = button.value;
            button.form.appendChild(hiddenSubmitValue);
        }
        button.dataset.originalContent = button.innerHTML;
        button.dataset.loadingApplied = 'true';
        if (button.tagName.toLowerCase() === 'button') {
            button.innerHTML = '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span><span>' + (label || 'Loading...') + '</span>';
        }
    }

    function getCookie(name) {
        return document.cookie.split(';').map(function (cookie) {
            return cookie.trim();
        }).reduce(function (value, cookie) {
            if (value || cookie.indexOf(name + '=') !== 0) {
                return value;
            }
            return decodeURIComponent(cookie.slice(name.length + 1));
        }, '');
    }

    function ensureCsrfField(form) {
        if (!form || (form.method || '').toLowerCase() !== 'post') {
            return;
        }
        var csrfInput = form.querySelector('input[name="csrfmiddlewaretoken"]');
        var csrfToken = csrfInput && csrfInput.value ? csrfInput.value : getCookie('csrftoken');
        if (!csrfToken) {
            return;
        }
        if (!csrfInput) {
            csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            form.appendChild(csrfInput);
        }
        csrfInput.value = csrfToken;
    }

    document.querySelectorAll('form').forEach(function (form) {
        form.addEventListener('submit', function (event) {
            var submitter = event.submitter || form.querySelector('button[type="submit"], input[type="submit"]');

            ensureCsrfField(form);
            var loadingText = form.dataset.loadingText || (submitter && submitter.dataset.loadingText) || 'Saving...';
            setButtonLoading(submitter, loadingText);
            if (form.dataset.showLoading === 'true') {
                showLoading(form.dataset.loadingMessage || loadingText);
            }
        });
    });

    document.querySelectorAll('[data-loading-screen]').forEach(function (link) {
        link.addEventListener('click', function () {
            showLoading(link.dataset.loadingMessage || 'Preparing your download...');
        });
    });

    document.querySelectorAll('[data-confirm]').forEach(function (trigger) {
        trigger.addEventListener('click', function (event) {
            if (!confirmModal || !confirmAction) {
                return;
            }
            event.preventDefault();
            confirmAction.href = trigger.getAttribute('href') || '#';
            confirmAction.className = 'btn ' + (trigger.dataset.confirmButtonClass || 'btn-danger');
            confirmAction.textContent = trigger.dataset.confirmButtonText || 'Confirm';
            if (confirmTitle) {
                confirmTitle.textContent = trigger.dataset.confirmTitle || 'Confirm action';
            }
            if (confirmMessage) {
                confirmMessage.textContent = trigger.dataset.confirmMessage || 'This action cannot be undone.';
            }
            confirmModal.show();
        });
    });
})();
