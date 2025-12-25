/* static/js/ajax_table.js */

document.addEventListener('DOMContentLoaded', function() {
    function updateTable(url, tableId) {
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.text())
        .then(html => {
            document.getElementById(tableId).innerHTML = html;
            attachEventListeners(tableId);
        })
        .catch(error => console.error('Error:', error));
    }

    function attachEventListeners(tableId) {
        document.querySelectorAll(`#${tableId} .pagination-link, #${tableId} .sort-link`).forEach(link => {
            link.addEventListener('click', function(event) {
                event.preventDefault();
                const url = this.href;
                updateTable(url, tableId);
            });
        });

        document.querySelectorAll(`#${tableId} .records-per-page-selector`).forEach(selector => {
            selector.addEventListener('change', function() {
                const form = this.closest('form');
                const url = new URL(form.action);
                const params = new URLSearchParams(new FormData(form));
                url.search = params.toString();
                updateTable(url.toString(), tableId);
            });
        });
    }

    document.querySelectorAll('.ajax-table').forEach(table => {
        attachEventListeners(table.id);
    });
});
