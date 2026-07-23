document.querySelectorAll('.notification-tab').forEach(function(tab) {
    tab.addEventListener('click', function() {
        var filter = tab.dataset.filter;
        var visibleCount = 0;

        document.querySelectorAll('.notification-tab').forEach(function(item) {
            item.classList.toggle('active', item === tab);
        });

        document.querySelectorAll('.notification-row').forEach(function(row) {
            var shouldShow = filter === 'all' || row.dataset.state === filter;
            row.hidden = !shouldShow;
            if (shouldShow) visibleCount += 1;
        });

        var filterEmpty = document.getElementById('filterEmpty');
        if (filterEmpty) {
            filterEmpty.hidden = visibleCount !== 0 || document.querySelectorAll('.notification-row').length === 0;
        }
    });
});
