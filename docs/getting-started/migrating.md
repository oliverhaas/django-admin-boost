# Migrating from django.contrib.admin

This guide covers switching from Django's built-in admin to `django_admin_boost.admin`. The migration is designed to be zero-friction — your existing `ModelAdmin` classes, templates, and third-party admin packages continue to work without changes.

## 1. Install django-admin-boost

```console
pip install django-admin-boost[jinja2]
```

## 2. Update settings.py

Replace `django.contrib.admin` with `django_admin_boost.admin` in `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # "django.contrib.admin",       # remove this
    "django_admin_boost.admin",          # add this
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    ...
]
```

Add the Jinja2 template backend **before** the DTL backend:

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "APP_DIRS": True,
        "OPTIONS": {
            "environment": "django_admin_boost.admin.jinja2_env.environment",
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

If you don't want Jinja2, just keep the DTL backend — django-admin-boost works with both.

## 3. Update admin.py imports

```python
# Before
from django.contrib import admin

# After
import django_admin_boost.admin as admin
```

Everything else stays the same — `@admin.register()`, `admin.ModelAdmin`, `admin.TabularInline`, `admin.site`, etc.

## 4. Update urls.py (optional)

```python
# Before
from django.contrib import admin

# After (optional — the old import still works via monkey-patching)
from django_admin_boost.admin import site

urlpatterns = [
    path("admin/", site.urls),
]
```

The old `from django.contrib import admin` / `admin.site.urls` pattern continues to work because `django_admin_boost.admin` redirects Django's admin site singleton. But using the direct import is cleaner.

## That's it

No database migrations needed — `django_admin_boost.admin` shares the same `django_admin_log` table.

No template changes needed — your custom admin templates continue to work (DTL templates are found via the DTL backend fallback).

Third-party admin packages (`django-import-export`, `django-debug-toolbar`, etc.) continue to work — they register on Django's admin site singleton, which is redirected to ours.

## What you get

- All admin pages rendered via Jinja2 (faster template rendering)
- `ListOnlyFieldsMixin` baked into `ModelAdmin` — set `list_only_fields` to optimize changelist queries
- `EstimatedCountPaginator` baked in — fast `pg_class.reltuples` counts on PostgreSQL
- DTL fallback for any template that doesn't have a Jinja2 version yet

## FAQ

**Do I need to keep `django.contrib.admin` in INSTALLED_APPS?**
No. Remove it entirely. `django_admin_boost.admin` is a complete standalone replacement.

**Will my existing admin log entries be preserved?**
Yes. `django_admin_boost.admin` uses the same `django_admin_log` database table.

**What about `django.contrib.auth`'s User/Group admin?**
They register automatically on our admin site via the monkey-patched singleton. You'll see Users and Groups in the admin as usual.

**Can I use django-admin-boost's mixins without the full replacement?**
Yes. Just `pip install django-admin-boost` (no `[jinja2]` extra needed) and use the mixins directly with stock Django admin:

```python
from django.contrib.admin import ModelAdmin
from django_admin_boost import ListOnlyFieldsMixin

class MyAdmin(ListOnlyFieldsMixin, ModelAdmin):
    list_only_fields = ["id", "name"]
```
