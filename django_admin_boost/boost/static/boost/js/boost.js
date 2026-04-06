/* Boost Admin — theme persistence and UI glue */
document.addEventListener('alpine:init', () => {
    Alpine.store('theme', {
        current: localStorage.getItem('boost-theme') || 'light',
        set(name) {
            this.current = name;
            document.documentElement.setAttribute('data-theme', name);
            localStorage.setItem('boost-theme', name);
        },
        init() {
            document.documentElement.setAttribute('data-theme', this.current);
        }
    });
});

/* Select-all checkbox for actions */
document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('action-toggle');
    if (toggle) {
        toggle.addEventListener('change', (e) => {
            document.querySelectorAll('input.action-select').forEach(cb => {
                cb.checked = e.target.checked;
            });
        });
    }
});
