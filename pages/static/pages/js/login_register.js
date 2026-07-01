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
    alertError.style.display = 'none';
    alertSuccess.style.display = 'none';
  }

  function showError(message) {
    alertErrorText.textContent = message;
    alertError.style.display = 'block';
    alertSuccess.style.display = 'none';
  }

  function showSuccess(message) {
    alertSuccessText.textContent = message;
    alertSuccess.style.display = 'block';
    alertError.style.display = 'none';
  }

  // Switch between login / register / forgot / reset panels
  function showPanel(name) {
    panels.forEach(function (p) {
      p.style.display = (p.dataset.panel === name) ? 'block' : 'none';
    });
    // Tab switcher only has login/register buttons — highlight the
    // matching one, or clear highlighting if we're on forgot/reset.
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
      const input = document.getElementById(btn.dataset.target);
      if (!input) return;
      const isHidden = input.type === 'password';
      input.type = isHidden ? 'text' : 'password';
      btn.textContent = isHidden ? 'Hide' : 'Show';
      btn.setAttribute('aria-label', isHidden ? 'Hide password' : 'Show password');
    });
  });

  // If the URL has ?resetToken=..., jump straight to the reset panel
  // and stash the token in the hidden field (mirrors the JSX useEffect).
  const resetToken = new URLSearchParams(window.location.search).get('resetToken');
  if (resetToken) {
    showPanel('reset');
    document.getElementById('reset-token').value = resetToken;
  }

  // --- Placeholder submit handlers -----------------------------------
  // No backend is wired up yet (screens-only phase). Each handler just
  // prevents the default page reload so you can see the UI behave.
  // Replace the body of each handler with a real fetch()/API call once
  // your Django auth views and endpoints exist.

  const loginForm = document.getElementById('form-login');
  loginForm.addEventListener('submit', function (e) {
    e.preventDefault();
    clearFieldErrors();
    hideAlerts();
    console.log('[login] submit — not yet connected to backend.');
  });

  const registerForm = document.getElementById('form-register');
  registerForm.addEventListener('submit', function (e) {
    e.preventDefault();
    clearFieldErrors();
    hideAlerts();
    console.log('[register] submit — not yet connected to backend.');
  });

  const forgotForm = document.getElementById('form-forgot');
  forgotForm.addEventListener('submit', function (e) {
    e.preventDefault();
    clearFieldErrors();
    hideAlerts();
    console.log('[forgot-password] submit — not yet connected to backend.');
  });

  const resetForm = document.getElementById('form-reset');
  resetForm.addEventListener('submit', function (e) {
    e.preventDefault();
    clearFieldErrors();
    hideAlerts();
    console.log('[reset-password] submit — not yet connected to backend.');
  });

});