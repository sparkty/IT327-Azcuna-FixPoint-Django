document.addEventListener('DOMContentLoaded', function() {
    const deleteBtn = document.querySelector('.btn-sm.danger');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', function() {
            document.getElementById('delete-form').style.display = 'block';
            this.style.display = 'none';
        });
    }
});
