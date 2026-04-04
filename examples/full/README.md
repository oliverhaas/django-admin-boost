# Full Example

`django_adminx.admin` with third-party admin packages:

- **django-import-export** — CSV/Excel import & export from the admin
- **django-simple-history** — full model change history with revert

## Setup

```bash
cd examples/full
uv sync
uv run python manage.py migrate
uv run python seed.py
uv run python manage.py runserver
```

Open http://localhost:8000/admin/ — log in with **admin / admin**.

## What to try

- **Import/Export**: Go to Products, click "Import" or "Export" buttons
- **History**: Edit a product, save, then click "History" to see changes with revert option
- **list_only_fields**: Products changelist uses optimized queries
