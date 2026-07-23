function setTabState(button, isActive) {
    if (!button) return;

    button.classList.toggle('active', isActive);
    button.setAttribute('aria-selected', String(isActive));
}

function switchTab(tab) {
    var panelIssues = document.getElementById('panel-issues');
    var panelMyIssues = document.getElementById('panel-my-issues');
    var panelUsers = document.getElementById('panel-users');

    if (panelIssues) panelIssues.style.display = tab === 'issues' ? '' : 'none';
    if (panelMyIssues) panelMyIssues.style.display = tab === 'my-issues' ? '' : 'none';
    if (panelUsers) panelUsers.style.display = tab === 'users' ? '' : 'none';

    setTabState(document.getElementById('tab-btn-issues'), tab === 'issues');
    setTabState(document.getElementById('tab-btn-my-issues'), tab === 'my-issues');
    setTabState(document.getElementById('tab-btn-users'), tab === 'users');
}

function getIssueFilters(prefix) {
    return {
        search: (document.getElementById(prefix.searchId)?.value || '').toLowerCase().trim(),
        status: document.getElementById(prefix.statusId)?.value || 'ALL',
        category: document.getElementById(prefix.categoryId)?.value || 'ALL',
        priority: document.getElementById(prefix.priorityId)?.value || 'ALL',
    };
}

function issueMatchesFilters(row, filters) {
    var title = row.dataset.title || '';
    var desc = row.dataset.desc || '';
    var status = row.dataset.status || '';
    var category = row.dataset.category || '';
    var priority = row.dataset.priority || '';

    var matchesSearch = !filters.search || title.includes(filters.search) || desc.includes(filters.search);
    var matchesStatus = filters.status === 'ALL' || status === filters.status;
    var matchesCategory = filters.category === 'ALL' || category === filters.category;
    var matchesPriority = filters.priority === 'ALL' || priority === filters.priority;

    return matchesSearch && matchesStatus && matchesCategory && matchesPriority;
}

function filterIssuePanel(panelSelector, emptyMessageId, filterIds) {
    var filters = getIssueFilters(filterIds);
    var rows = document.querySelectorAll(panelSelector + ' .issue-row');
    var visible = 0;

    rows.forEach(function(row) {
        var show = issueMatchesFilters(row, filters);
        row.style.display = show ? '' : 'none';
        if (show) visible++;
    });

    var noMsg = document.getElementById(emptyMessageId);
    if (noMsg) noMsg.style.display = visible === 0 ? '' : 'none';
}

function filterIssues() {
    filterIssuePanel('#panel-issues', 'no-issues-msg', {
        searchId: 'issue-search',
        statusId: 'filter-status',
        categoryId: 'filter-category',
        priorityId: 'filter-priority',
    });
}

function filterMyIssues() {
    filterIssuePanel('#panel-my-issues', 'my-no-issues-msg', {
        searchId: 'my-issue-search',
        statusId: 'my-filter-status',
        categoryId: 'my-filter-category',
        priorityId: 'my-filter-priority',
    });
}

function toggleUser(userId) {
    var issuesDiv = document.getElementById('user-issues-' + userId);
    var chevron = document.getElementById('chevron-' + userId);
    var btn = document.getElementById('user-btn-' + userId);

    if (!issuesDiv) return;

    var isExpanded = issuesDiv.style.display !== 'none';
    issuesDiv.style.display = isExpanded ? 'none' : '';
    if (chevron) chevron.textContent = isExpanded ? '+' : '-';
    if (btn) btn.setAttribute('aria-expanded', String(!isExpanded));
}

function filterUsers() {
    var search = (document.getElementById('user-search')?.value || '').toLowerCase().trim();
    var status = document.getElementById('user-filter-status')?.value || 'ALL';
    var category = document.getElementById('user-filter-category')?.value || 'ALL';
    var priority = document.getElementById('user-filter-priority')?.value || 'ALL';
    var noFilters = !search && status === 'ALL' && category === 'ALL' && priority === 'ALL';
    var visibleGroups = 0;

    document.querySelectorAll('.user-group').forEach(function(group) {
        if (noFilters) {
            group.style.display = '';
            group.querySelectorAll('.user-issue-row').forEach(function(row) {
                row.style.display = '';
            });
            visibleGroups++;
            return;
        }

        var name = group.dataset.name || '';
        var email = group.dataset.email || '';
        var nameEmailMatch = !search || name.includes(search) || email.includes(search);
        var visibleIssues = 0;

        group.querySelectorAll('.user-issue-row').forEach(function(row) {
            var title = row.dataset.title || '';
            var matchesSearch = !search || nameEmailMatch || title.includes(search);
            var matchesStatus = status === 'ALL' || row.dataset.status === status;
            var matchesCategory = category === 'ALL' || row.dataset.category === category;
            var matchesPriority = priority === 'ALL' || row.dataset.priority === priority;
            var show = matchesSearch && matchesStatus && matchesCategory && matchesPriority;

            row.style.display = show ? '' : 'none';
            if (show) visibleIssues++;
        });

        var hasIssueFilters = status !== 'ALL' || category !== 'ALL' || priority !== 'ALL';
        var showGroup = hasIssueFilters ? visibleIssues > 0 : nameEmailMatch;
        group.style.display = showGroup ? '' : 'none';
        if (showGroup) visibleGroups++;
    });

    var noUsersMsg = document.getElementById('no-users-msg');
    if (noUsersMsg) noUsersMsg.style.display = visibleGroups === 0 ? '' : 'none';
}

function exportIssues() {
    alert('Export functionality coming soon.');
}

function openDeletionModal(deleteRequestId, issueTitle, requesterName, reason) {
    var backdrop = document.getElementById('deletion-modal-backdrop');
    if (!backdrop) return;

    document.getElementById('modal-issue-title').textContent = issueTitle;
    document.getElementById('modal-requester-name').textContent = requesterName;
    document.getElementById('modal-reason-text').textContent = reason;

    document.getElementById('deletion-accept-form').action = '/deletion-request/' + deleteRequestId + '/accept/';
    document.getElementById('deletion-cancel-form').action = '/deletion-request/' + deleteRequestId + '/cancel/';
    backdrop.style.display = 'flex';
}

function closeDeletionModal() {
    var backdrop = document.getElementById('deletion-modal-backdrop');
    if (backdrop) backdrop.style.display = 'none';
}
