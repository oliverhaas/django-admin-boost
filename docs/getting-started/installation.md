# Installation

```console
pip install django-adminx
```

For Jinja2 support:

```console
pip install django-adminx[jinja2]
```

## Full admin replacement

Replace `django.contrib.admin` with `django_adminx.admin` in your settings:

```python
INSTALLED_APPS = [
    "django_adminx.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
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

Then use `django_adminx.admin` instead of `django.contrib.admin` in your admin modules:

```python
import django_adminx.admin as admin

@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "created_at"]
```

## Standalone mixins only

If you just want the performance mixins with stock Django admin:

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    ...
]
```

```python
from django.contrib.admin import ModelAdmin
from django_adminx import ListOnlyFieldsMixin, EstimatedCountPaginator

class MyModelAdmin(ListOnlyFieldsMixin, ModelAdmin):
    list_only_fields = ["id", "name", "status"]
    paginator = EstimatedCountPaginator
```

No app registration needed — just import the mixins.
