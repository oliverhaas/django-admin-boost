# Unmanaged Admin

`django_admin_boost.unmanaged` is a thin kernel for building Django admin pages
backed by data that doesn't live in the relational database — caches, in-memory
state, Redis keys, third-party APIs, anything you can iterate.

Three abstract base classes:

- [`UnmanagedModel`](#unmanagedmodel) — a `models.Model` subclass with `managed = False`
  forced. Used as a stand-in so Django's admin URL routing, permission machinery,
  and template rendering all work normally.
- [`UnmanagedQuerySet`](#unmanagedqueryset) — satisfies just enough of the QuerySet
  protocol for `ChangeList` and `Paginator` to render against it.
- [`UnmanagedModelAdmin`](#unmanagedmodeladmin) — a `ModelAdmin` with read-only
  defaults, `delete_selected` stripped, and a hook for smuggling custom GET
  params past `ChangeList`'s strict lookup parser.

No concrete data backings, no list-backed default, no cursor paginator, no
templates. You bring the data, the kernel does the plumbing.

## When to use it

When you want a Django admin page over data that isn't a database table —
without inventing a parallel UI. Common cases: cache inspectors, queue/job
dashboards, configuration browsers, third-party API explorers.

If your data does live in a database table, use a regular `ModelAdmin`.

## UnmanagedModel

```python
from django.db import models
from django_admin_boost.unmanaged import UnmanagedModel, UnmanagedModelMeta

class CacheEntry(UnmanagedModel):
    key = models.CharField(max_length=200, primary_key=True)
    value = models.CharField(max_length=200)
    hits = models.IntegerField(default=0)

    class Meta(UnmanagedModelMeta):
        app_label = "mycache"
```

- `Meta(UnmanagedModelMeta)` injects `managed = False` automatically.
- `app_label` must be set explicitly (Django requires it for any concrete model
  declared outside an installed app).
- `save()` and `delete()` raise `UnmanagedModelError`.
- `__str__` defaults to `str(self.pk)` — override as needed.

### Registering an admin

```python
class CacheEntryAdmin(UnmanagedModelAdmin):
    ...

CacheEntry.register(CacheEntryAdmin)
# or
CacheEntry.register(CacheEntryAdmin, site=my_admin_site)
```

`register()` defaults to `django.contrib.admin.site`. Equivalent to plain
`admin.site.register(CacheEntry, CacheEntryAdmin)`.

## UnmanagedQuerySet

Subclasses MUST implement:

- `count() -> int`
- `__iter__() -> Iterator[Any]`
- `__getitem__(key: int | slice) -> Any`
- `filter(*args, pk__in=None, **kwargs) -> Self`
- `order_by(*fields: str) -> Self`

Everything else (`select_related`, `distinct`, `alias`, `only`, `defer`,
`_clone`, `_next_is_sticky`, `all`) is provided as a no-op that returns `self`.
The `query` attribute is a stub with `select_related = False` and
`order_by = ()` so `ChangeList` can inspect it safely.

```python
from django_admin_boost.unmanaged import UnmanagedQuerySet

class CacheEntryQuerySet(UnmanagedQuerySet):
    def __init__(self, model, cache_alias):
        super().__init__(model)
        self._cache = caches[cache_alias]

    def count(self):
        return len(self._cache.keys("*"))

    def __iter__(self):
        for key in self._cache.keys("*"):
            yield CacheEntry(key=key, value=self._cache.get(key))

    def __getitem__(self, key):
        return list(self)[key]

    def filter(self, *args, pk__in=None, **kwargs):
        if pk__in is None:
            return self
        ...

    def order_by(self, *fields):
        return self
```

## UnmanagedModelAdmin

```python
from django_admin_boost.unmanaged import UnmanagedModelAdmin

class CacheEntryAdmin(UnmanagedModelAdmin):
    list_display = ["key", "value", "hits"]

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def get_queryset(self, request):
        return CacheEntryQuerySet(CacheEntry, cache_alias="default")
```

Defaults baked in (override any of them):

| Behaviour                  | Default                                           |
|----------------------------|---------------------------------------------------|
| `has_add_permission`       | `False`                                           |
| `has_change_permission`    | `False`                                           |
| `has_delete_permission`    | `False`                                           |
| `get_actions`              | strips `delete_selected`                          |
| `actions`                  | `[]` (so subclasses can append)                   |
| `list_per_page`            | `100`                                             |
| `get_queryset`             | raises `NotImplementedError`                      |

### Custom GET parameters

`ChangeList` parses every GET param as a field lookup and raises
`IncorrectLookupParameters` for anything it doesn't recognise. To accept extra
params (cursors, help flags, etc.), list them on `extra_changelist_params`:

```python
class CacheEntryAdmin(UnmanagedModelAdmin):
    extra_changelist_params = ("cursor",)

    def changelist_view(self, request, extra_context=None):
        cursor = getattr(request, "_unmanaged_params", {}).get("cursor")
        ...
        return super().changelist_view(request, extra_context)
```

The named params are popped off `request.GET` before `ChangeList` sees them
and stashed on `request._unmanaged_params` as `dict[str, str]`.

### Suppressing pagination

Set `disable_list_pagination = True` to suppress the page-number chrome —
useful when the queryset returns the full list every time or paginates
internally via cursor.

```python
class CacheEntryAdmin(UnmanagedModelAdmin):
    disable_list_pagination = True
```

Under the hood, `get_paginator` returns a `Paginator` subclass whose
`num_pages` is always `1`.

## Read-only change views

With the default `has_change_permission = False`, the per-row detail page
renders as a view-only page (no Save button) automatically. To enrich it,
set `readonly_fields` and `fieldsets` as you would on a regular `ModelAdmin`.

## Not an app

The `unmanaged` subpackage is not a Django app and doesn't need to be added
to `INSTALLED_APPS`. Your unmanaged model lives in your own app — the
kernel just provides the base classes.
