# Simple Example

Basic shop project using `django_admin_boost.admin` with Jinja2 templates. No third-party admin packages.

## Setup

```bash
cd examples/simple
uv sync
uv run python manage.py migrate
uv run python seed.py
uv run python manage.py runserver
```

Open http://localhost:8000/admin/ — log in with **admin / admin**.

## What's in the box

- **Categories** — simple model with list_editable sort order
- **Tags** — minimal model (just a name)
- **Products** — FK, M2M, choices, date_hierarchy, fieldsets, inlines, search, filters, list_only_fields
- **Customers** — search, readonly fields
- **Orders** — FK to customer, status filter, date_hierarchy, inline order items
