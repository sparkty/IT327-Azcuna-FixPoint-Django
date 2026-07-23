document.addEventListener('DOMContentLoaded', function () {
  const tabButtons = document.querySelectorAll('.auth-tab-btn');
  const panels = document.querySelectorAll('.auth-form');
  const alertError = document.getElementById('alert-error');
  const alertErrorText = document.getElementById('alert-error-text');
  const alertSuccess = document.getElementById('alert-success');
  const alertSuccessText = document.getElementById('alert-success-text');

  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function clearFieldErrors() {
    document.querySelectorAll('.field-error').forEach(function (el) {
      el.textContent = '';
    });
    document.querySelectorAll('.input-error').forEach(function (el) {
      el.classList.remove('input-error');
    });
  }

  function hideAlerts() {
    if (alertError) alertError.style.display = 'none';
    if (alertSuccess) alertSuccess.style.display = 'none';
  }

  function showError(message) {
    if (alertErrorText) alertErrorText.textContent = message;
    if (alertError) alertError.style.display = 'block';
    if (alertSuccess) alertSuccess.style.display = 'none';
  }

  function showSuccess(message) {
    if (alertSuccessText) alertSuccessText.textContent = message;
    if (alertSuccess) alertSuccess.style.display = 'block';
    if (alertError) alertError.style.display = 'none';
  }

  // Switch between login / register / forgot / reset panels
  function showPanel(name) {
    panels.forEach(function (p) {
      p.style.display = (p.dataset.panel === name) ? 'block' : 'none';
    });
    tabButtons.forEach(function (b) {
      b.classList.toggle('active', b.dataset.tab === name);
    });
    hideAlerts();
    clearFieldErrors();
  }

  tabButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      showPanel(btn.dataset.tab);
    });
  });

  // "Forgot password?" link and "Back to sign in" buttons
  document.querySelectorAll('[data-switch-to]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      e.preventDefault();
      showPanel(el.dataset.switchTo);
    });
  });

  // Password show/hide toggles
  document.querySelectorAll('.password-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const targetId = btn.dataset.target;
      const input = document.getElementById(targetId);
      if (!input) return;
      const isHidden = input.type === 'password';
      input.type = isHidden ? 'text' : 'password';
      btn.textContent = isHidden ? 'Hide' : 'Show';
      btn.setAttribute('aria-label', isHidden ? 'Hide password' : 'Show password');
    });
  });

  // If the URL has ?resetToken=..., jump straight to the reset panel
  const resetToken = new URLSearchParams(window.location.search).get('resetToken');
  if (resetToken) {
    showPanel('reset');
    const resetTokenInput = document.getElementById('reset-token');
    if (resetTokenInput) resetTokenInput.value = resetToken;
  }

  // ── LOGIN HANDLER ──────────────────────────────────────────────────
  const loginForm = document.getElementById('form-login');
  if (loginForm) {
    loginForm.addEventListener('submit', function (e) {
      console.log('Login form submitting...');
    });
  }

  // ── REGISTER HANDLER ──────────────────────────────────────────────
  const registerForm = document.getElementById('form-register');
  if (registerForm) {
    registerForm.addEventListener('submit', function (e) {
      console.log('Register form submitting...');
    });
  }

  // ── FORGOT PASSWORD HANDLER ──────────────────────────────────────

  // ── RESET PASSWORD HANDLER ───────────────────────────────────────
  const resetForm = document.getElementById('form-reset');
  if (resetForm) {
    resetForm.addEventListener('submit', function (e) {
      const password = document.getElementById('reset-password').value;
      const confirmPassword = document.getElementById('reset-confirm-password').value;

      if (!password || password.length < 8) {
        e.preventDefault();
        showError('Password must be at least 8 characters.');
        return;
      }
      if (password !== confirmPassword) {
        e.preventDefault();
        showError('Passwords do not match.');
        return;
      }
      // Passes — let the form POST to /reset-password/ naturally.
    });
  }

  // ── Display Django messages from the server ──────────────────────
  const djangoMessages = document.querySelectorAll('.alert-success, .alert-error');
  djangoMessages.forEach(function(msg) {
    if (msg.classList.contains('alert-success')) {
      msg.style.display = 'block';
    }
    if (msg.classList.contains('alert-error')) {
      msg.style.display = 'block';
    }
  });
});