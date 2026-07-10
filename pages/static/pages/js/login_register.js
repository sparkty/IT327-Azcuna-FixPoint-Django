document.addEventListener('DOMContentLoaded', function () {
  const tabButtons = document.querySelectorAll('.auth-tab-btn');
  const panels = document.querySelectorAll('.auth-form');
  const alertError = document.getElementById('alert-error');
  const alertErrorText = document.getElementById('alert-error-text');
  const alertSuccess = document.getElementById('alert-success');
  const alertSuccessText = document.getElementById('alert-success-text');

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
      // Let the form submit naturally - no need to prevent default
      // The form will POST to the server and handle the redirect
      console.log('Login form submitting...');
    });
  }

  // ── REGISTER HANDLER ──────────────────────────────────────────────
  const registerForm = document.getElementById('form-register');
  if (registerForm) {
    registerForm.addEventListener('submit', function (e) {
      // Let the form submit naturally
      console.log('Register form submitting...');
    });
  }

  // ── FORGOT PASSWORD HANDLER ──────────────────────────────────────
  const forgotForm = document.getElementById('form-forgot');
  if (forgotForm) {
    forgotForm.addEventListener('submit', function (e) {
      e.preventDefault();
      clearFieldErrors();
      hideAlerts();

      const email = document.getElementById('forgot-email').value.trim();

      if (!email) {
        showError('Email is required.');
        return;
      }

      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

      fetch('/forgot-password/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': csrftoken,
        },
        body: new URLSearchParams({
          'email': email,
        }),
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          showSuccess('If that email exists, a reset link has been sent.');
        } else {
          showError(data.message || 'Failed to send reset link.');
        }
      })
      .catch(() => {
        showError('Failed to send reset link. Please try again.');
      });
    });
  }

  // ── RESET PASSWORD HANDLER ───────────────────────────────────────
  const resetForm = document.getElementById('form-reset');
  if (resetForm) {
    resetForm.addEventListener('submit', function (e) {
      e.preventDefault();
      clearFieldErrors();
      hideAlerts();

      const password = document.getElementById('reset-password').value;
      const confirmPassword = document.getElementById('reset-confirm-password').value;
      const token = document.getElementById('reset-token').value;

      if (!password || password.length < 8) {
        showError('Password must be at least 8 characters.');
        return;
      }
      if (password !== confirmPassword) {
        showError('Passwords do not match.');
        return;
      }

      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

      fetch('/reset-password/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': csrftoken,
        },
        body: new URLSearchParams({
          'token': token,
          'password': password,
        }),
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          showSuccess('Password reset successfully. Please sign in.');
          setTimeout(() => showPanel('login'), 1500);
        } else {
          showError(data.message || 'Reset link is invalid or expired.');
        }
      })
      .catch(() => {
        showError('Failed to reset password. Please try again.');
      });
    });
  }

  // ── Display Django messages from the server ──────────────────────
  // If there are Django messages, they'll be shown as alerts
  const djangoMessages = document.querySelectorAll('.alert-success, .alert-error');
  djangoMessages.forEach(function(msg) {
    // They're already displayed by Django, but we want to ensure they show
    if (msg.classList.contains('alert-success')) {
      msg.style.display = 'block';
    }
    if (msg.classList.contains('alert-error')) {
      msg.style.display = 'block';
    }
  });
});