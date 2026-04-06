# Approximate Count Display — Design Spec

**Issue:** [#2 — Display estimated counts with ~ prefix in changelist templates](https://github.com/oliverhaas/django-admin-boost/issues/2)
**Date:** 2026-04-06

## Problem

When `EstimatedCountPaginator` returns an estimate from `pg_class.reltuples`, the admin displays it as an exact count (e.g., "1,200 articles"). Users can't tell whether the count is precise or approximate.

## Solution

Add `is_approximate_count` to `EstimatedCountPaginator`. When `True`, admin templates display the count with a `~` prefix (e.g., "~1,200 articles").

## Paginator changes

**File:** `django_admin_boost/paginators.py`

Add a private `_used_estimate: bool = False` attribute. The existing `count` cached property sets it to `True` when it returns an estimate from `pg_class.reltuples`. A public `is_approximate_count` property reads it, triggering `count` computation if needed.

```python
class EstimatedCountPaginator(Paginator):
    _used_estimate: bool = False

    @cached_property
    def count(self) -> int:
        queryset = self.object_list
        if not isinstance(queryset, QuerySet):
            return len(self.object_list)
        if self._can_use_estimate(queryset):
            estimate = self._get_estimate(queryset)
            if estimate is not None and estimate > 0:
                self._used_estimate = True
                return int(estimate)
        return queryset.count()

    @property
    def is_approximate_count(self) -> bool:
        _ = self.count  # ensure count is computed
        return self._used_estimate
```

The `is_approximate_count` property is safe to call at any point — accessing `self.count` triggers the cached property if not yet computed. When the queryset has WHERE clauses (filters/search active), `_can_use_estimate` returns `False`, so `_used_estimate` stays `False` and `is_approximate_count` returns `False`.

## Template changes

Four template files are modified (Jinja2 + DTL pairs):

### `pagination.html` — result count display

The count shown at the bottom of the changelist (e.g., "1,200 articles") gets a `~` prefix when approximate.

**Jinja2** (`admin/jinja2/admin/pagination.html`), line 10 changes from:
```
{{ cl.result_count }}
```
to:
```
{% if cl.paginator.is_approximate_count %}~{% endif %}{{ cl.result_count }}
```

**DTL** (`admin/templates/admin/pagination.html`) — same change with DTL syntax.

### `actions.html` — "Select all N items" text

The "Select all 1,200 articles" link in the actions bar gets the same `~` prefix.

**Jinja2** (`admin/jinja2/admin/actions.html`), the `result_count` reference in the "Select all" text gets the `~` prefix.

**DTL** (`admin/templates/admin/actions.html`) — same change with DTL syntax.

### Templates NOT changed

- `search_form.html` — search results are always exact counts (filtered queries use real `COUNT(*)`)
- `change_list.html` — no direct count display

## What doesn't change

- `SmartPaginatorMixin` — untouched
- `ListFieldsMixin` — untouched
- `ChangeList` / `result_count` — the flag lives on the paginator, not the changelist
- `show_full_result_count` — stays `False` in `SmartPaginatorMixin`

## Behavior summary

| Scenario | `is_approximate_count` | Display |
|---|---|---|
| PostgreSQL, unfiltered, estimate > 0 | `True` | ~1,200 articles |
| PostgreSQL, filtered/search active | `False` | 3 articles |
| PostgreSQL, estimate ≤ 0 (fresh table) | `False` | 0 articles |
| Non-PostgreSQL (SQLite, MySQL) | `False` | 1,200 articles |
| Non-QuerySet object_list | `False` | 5 items |
