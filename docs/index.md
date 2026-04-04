# Django AdminX

Drop-in replacement for `django.contrib.admin` that works with Jinja2 (and DTL). Ships standalone performance mixins you can use with the stock Django admin too.

## Two ways to use it

### Full admin replacement

Replace `django.contrib.admin` entirely. All admin pages render via Jinja2 by default, with DTL fallback.

```python
INSTALLED_APPS = ["django_adminx.admin", ...]
```

```python
import django_adminx.admin as admin

@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    list_only_fields = ["id", "name", "status"]
```

### Standalone mixins

Keep stock Django admin, just add performance optimizations.

```python
from django.contrib.admin import ModelAdmin
from django_adminx import ListOnlyFieldsMixin, EstimatedCountPaginator

class MyModelAdmin(ListOnlyFieldsMixin, ModelAdmin):
    list_only_fields = ["id", "name", "status"]
    paginator = EstimatedCountPaginator
```

## What's included

| Feature | Standalone | Full admin |
|---------|-----------|------------|
| `ListOnlyFieldsMixin` — automatic `.only()` on changelist querysets | Yes | Baked in |
| `SmartPaginatorMixin` — PostgreSQL estimated counts | Yes | Baked in |
| `EstimatedCountPaginator` — `pg_class.reltuples` paginator | Yes | Baked in |
| Jinja2 admin templates (all 50) | — | Yes |
| DTL admin templates (fallback) | — | Yes |
| Drop-in `ModelAdmin`, `AdminSite`, `register` | — | Yes |
