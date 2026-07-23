// DOM refs
const $ = (id) => document.getElementById(id);
const errorAlert = $('errorAlert');
const successAlert = $('successAlert');
const errorMsg = $('errorMsg');
const successMsg = $('successMsg');
const locationNote = $('locationNote');
const attachmentsList = $('attachmentsList');
const previewAttachments = $('previewAttachments');
const previewDateTime = $('previewDateTime');
const submitBtn = $('submitBtn');
const submitBtnForm = $('submitBtnForm');
const issueForm = $('issueForm');

let attachments = [];
let loading = false;

// Initialize
function init() {
    updateDateTime();
    detectLocation();
    loadDraft();

    if (issueForm) {
        issueForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleSubmit();
        });
    }

    ['issueTitle', 'issueCategory', 'issuePriority', 'issueDescription'].forEach(id => {
        const el = $(id);
        if (el) el.addEventListener('input', hideAlerts);
    });
}

function updateDateTime() {
    const now = new Date();
    if (previewDateTime) {
        previewDateTime.textContent = `${now.toLocaleDateString()} · ${now.toLocaleTimeString()}`;
    }
}

function detectLocation() {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 6000);

    fetch('https://free.freeipapi.com/api/json', { signal: controller.signal })
        .then(res => res.json())
        .then(data => {
            if (data.cityName || data.regionName) {
                if (locationNote) {
                    locationNote.textContent = `🌐 Reporting from: ${[data.cityName, data.regionName].filter(Boolean).join(', ')}`;
                }
            } else {
                if (locationNote) locationNote.textContent = '🌐 Location unavailable';
            }
        })
        .catch(() => {
            if (locationNote) locationNote.textContent = '🌐 Location unavailable';
        })
        .finally(() => clearTimeout(timeoutId));
}

function handleFileUpload(e) {
    const files = Array.from(e.target.files);
    const newAttachments = files.map((file, index) => ({
        id: Date.now() + index,
        name: file.name,
        size: `${(file.size / 1024 / 1024).toFixed(2)} MB`,
        file: file
    }));
    attachments = [...attachments, ...newAttachments];
    renderAttachments();
    e.target.value = '';
}

function handleRemoveAttachment(id) {
    attachments = attachments.filter(att => att.id !== id);
    renderAttachments();
}

function renderAttachments() {
    if (attachments.length === 0) {
        if (attachmentsList) attachmentsList.innerHTML = '';
        if (previewAttachments) previewAttachments.textContent = '0 file(s) attached';
        return;
    }

    if (attachmentsList) {
        attachmentsList.innerHTML = attachments.map(file => `
            <div class="attachment-chip">
                📄 ${file.name} (${file.size})
                <span class="remove-attachment" onclick="handleRemoveAttachment(${file.id})">×</span>
            </div>
        `).join('');
    }

    if (previewAttachments) {
        previewAttachments.textContent = `${attachments.length} file(s) attached`;
    }
}

function handleSubmit() {
    const title = $('issueTitle')?.value || '';
    const category = $('issueCategory')?.value || '';
    const description = $('issueDescription')?.value || '';
    const priority = $('issuePriority')?.value || 'MEDIUM';

    if (!title.trim()) { showAlert('error', 'Issue title is required'); return; }
    if (!category) { showAlert('error', 'Please select a category'); return; }
    if (!description.trim()) { showAlert('error', 'Description is required'); return; }

    loading = true;
    if (submitBtn) { submitBtn.textContent = 'SUBMITTING...'; submitBtn.disabled = true; }
    if (submitBtnForm) { submitBtnForm.textContent = 'SUBMITTING...'; submitBtnForm.disabled = true; }
    hideAlerts();

    const formData = new FormData();
    formData.append('title', title);
    formData.append('category', category);
    formData.append('priority', priority);
    formData.append('description', description);

    attachments.forEach((att, index) => {
        formData.append(`attachment_${index}`, att.file);
    });

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    fetch(window.location.href, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken,
        },
    })
    .then(response => response.json())
    .then(data => {
        loading = false;
        if (submitBtn) { submitBtn.textContent = 'Submit Issue →'; submitBtn.disabled = false; }
        if (submitBtnForm) { submitBtnForm.textContent = 'SUBMIT ISSUE →'; submitBtnForm.disabled = false; }

        if (data.success) {
            showAlert('success', data.message);
            attachments = [];
            renderAttachments();

            if ($('issueTitle')) $('issueTitle').value = '';
            if ($('issueCategory')) $('issueCategory').value = '';
            if ($('issuePriority')) $('issuePriority').value = 'MEDIUM';
            if ($('issueDescription')) $('issueDescription').value = '';

            setTimeout(() => {
                window.location.href = `/issue/${data.issue_id}/`;
            }, 1500);
        } else {
            const errors = Object.values(data.errors).flat().join(', ');
            showAlert('error', errors || 'Failed to create issue. Please try again.');
        }
    })
    .catch(() => {
        loading = false;
        if (submitBtn) { submitBtn.textContent = 'Submit Issue →'; submitBtn.disabled = false; }
        if (submitBtnForm) { submitBtnForm.textContent = 'SUBMIT ISSUE →'; submitBtnForm.disabled = false; }
        showAlert('error', 'Failed to create issue. Please try again.');
    });
}

function handleSaveDraft() {
    const draft = {
        title: $('issueTitle')?.value || '',
        category: $('issueCategory')?.value || '',
        priority: $('issuePriority')?.value || 'MEDIUM',
        description: $('issueDescription')?.value || '',
        attachments: attachments.map(a => ({ name: a.name, size: a.size })),
        savedAt: new Date().toISOString()
    };
    localStorage.setItem('issueDraft', JSON.stringify(draft));
    showAlert('success', 'Draft saved locally!');
    setTimeout(hideAlerts, 2000);
}

function loadDraft() {
    try {
        const draft = JSON.parse(localStorage.getItem('issueDraft'));
        if (draft) {
            if ($('issueTitle')) $('issueTitle').value = draft.title || '';
            if ($('issueCategory')) $('issueCategory').value = draft.category || '';
            if ($('issuePriority')) $('issuePriority').value = draft.priority || 'MEDIUM';
            if ($('issueDescription')) $('issueDescription').value = draft.description || '';
        }
    } catch (e) { /* Ignore */ }
}

function showAlert(type, message) {
    if (type === 'error') {
        if (errorMsg) errorMsg.textContent = message;
        if (errorAlert) errorAlert.classList.remove('hidden');
        if (successAlert) successAlert.classList.add('hidden');
    } else {
        if (successMsg) successMsg.textContent = message;
        if (successAlert) successAlert.classList.remove('hidden');
        if (errorAlert) errorAlert.classList.add('hidden');
    }
}

function hideAlerts() {
    if (errorAlert) errorAlert.classList.add('hidden');
    if (successAlert) successAlert.classList.add('hidden');
}

document.addEventListener('DOMContentLoaded', init);
setInterval(updateDateTime, 60000);
