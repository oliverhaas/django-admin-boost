# Changelog

## 0.1.0a1 (Unreleased)

Initial release.

- Full drop-in replacement for `django.contrib.admin` with Jinja2 template support
- All 50 admin templates converted to Jinja2 with DTL fallback
- Standalone performance mixins: `ListOnlyFieldsMixin`, `SmartPaginatorMixin`
- `EstimatedCountPaginator` using PostgreSQL `pg_class.reltuples`
- Render-parity tests verifying output matches Django's original admin
