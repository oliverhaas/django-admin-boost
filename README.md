# django-adminx

[![PyPI version](https://img.shields.io/pypi/v/django-adminx.svg?style=flat)](https://pypi.org/project/django-adminx/)
[![Python versions](https://img.shields.io/pypi/pyversions/django-adminx.svg)](https://pypi.org/project/django-adminx/)
[![CI](https://github.com/oliverhaas/django-adminx/actions/workflows/ci.yml/badge.svg)](https://github.com/oliverhaas/django-adminx/actions/workflows/ci.yml)

Drop-in replacement for `django.contrib.admin` that works with Jinja2 (and DTL). Ships standalone performance mixins you can use with the stock Django admin too.

## Features

- **Jinja2 admin templates** — all 50 admin templates converted, with DTL fallback
- **Full drop-in replacement** — swap `django.contrib.admin` for `django_adminx.admin` and everything just works
- **Standalone performance mixins** — use `ListOnlyFieldsMixin` or `EstimatedCountPaginator` with stock Django admin, no full replacement needed
- **`list_only_fields`** — automatic `.only()` on changelist querysets
- **Smart paginator** — uses PostgreSQL's `pg_class.reltuples` for fast estimated counts on large tables

## Quick Start

### Full admin replacement (Jinja2)

```python
# settings.py
INSTALLED_APPS = [
    "django_adminx.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    ...
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "APP_DIRS": True,
        "OPTIONS": {
            "environment": "django_adminx.admin.jinja2_env.environment",
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
```

```python
# admin.py
import django_adminx.admin as admin

@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "created_at"]
    list_only_fields = ["id", "name", "status", "created_at"]
```

### Just the performance mixins (with stock Django admin)

```python
# settings.py
INSTALLED_APPS = ["django.contrib.admin", ...]
```

```python
# admin.py
from django.contrib.admin import ModelAdmin
from django_adminx import ListOnlyFieldsMixin, EstimatedCountPaginator

class MyModelAdmin(ListOnlyFieldsMixin, ModelAdmin):
    list_only_fields = ["id", "name", "status"]
    paginator = EstimatedCountPaginator
```

## Installation

```console
pip install django-adminx
```

For Jinja2 support:

```console
pip install django-adminx[jinja2]
```

## Documentation

Full documentation at [oliverhaas.github.io/django-adminx](https://oliverhaas.github.io/django-adminx/)

## License

MIT
