document.querySelectorAll('.profile-pw-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
        var targetId = btn.getAttribute('data-target');
        var input = document.getElementById(targetId);
        if (!input) return;
        var isHidden = input.type === 'password';
        input.type = isHidden ? 'text' : 'password';
        btn.textContent = isHidden ? 'Hide' : 'Show';
        btn.setAttribute('aria-label', isHidden ? 'Hide password' : 'Show password');
    });
});
