# Boost Admin Design

A custom Django admin UI built from scratch with Jinja2-native templates and DaisyUI components. Ships as `django_admin_boost.boost`.

## Goals

- Modern, clean admin UI using DaisyUI semantic CSS classes
- Jinja2-native templates (no DTL, no conversion artifacts)
- Unfold-level feature set (enhanced actions, inlines, tabs) on Django's ModelAdmin
- Dashboard widget system with optional HTMX lazy loading
- All DaisyUI themes work out of the box; light + dark curated as defaults
- Close to stock Django admin configuration surface (no settings dict)
- No upstream tracking burden — fully owned code

## Non-Goals (for v1)

- Collapsible sidebar navigation (future addition)
- Contrib modules for third-party packages (constance, import_export, etc.)
- DTL template fallback

## Architecture

### Python Layer

Copy unfold's Python code as starting point for the feature set (enhanced actions, tabs, nested inlines, etc.), then strip out unfold's theme/settings system. The Python layer sits on top of Django's ModelAdmin and AdminSite.

Key modules:
- `admin.py` — ModelAdmin subclass with unfold's enhanced features
- `sites.py` — AdminSite subclass with dashboard widget support
- `dashboard.py` — Widget base classes and registry
- `widgets.py` — DaisyUI-styled form widgets
- `forms.py` — Form overrides
- `fields.py` — Field overrides
- `decorators.py` — @register, @action, @display
- `checks.py` — System checks
- `jinja2_env.py` — Jinja2 environment factory

### Templates

Written from scratch in Jinja2. Estimated ~40-50 templates total. Templates use DaisyUI semantic classes, keeping them compact and readable.

#### Template Namespace

- `jinja2/admin/` — overrides Django's admin template namespace (base, change_list, change_form, etc.)
- `jinja2/boost/` — boost-specific partials (components, widgets, forms)

### Frontend Stack

- **DaisyUI + Tailwind CSS** — pre-compiled, shipped as `static/boost/css/boost.css`
- **Alpine.js** — dropdowns, theme toggle, action confirmations, inline interactions
- **HTMX** — dashboard lazy loading
- **Chart.js** — optional, loaded only by ChartWidget

No build step for users. Everything ships pre-built in `static/boost/`.

## Package Structure

```
django_admin_boost/
  boost/
    __init__.py
    apps.py
    admin.py
    sites.py
    widgets.py
    forms.py
    fields.py
    decorators.py
    checks.py
    dashboard.py
    templatetags/
      __init__.py
      boost.py
    jinja2/
      admin/
        base.html
        base_site.html
        index.html
        app_index.html
        change_list.html
        change_form.html
        change_form_object_tools.html
        change_list_object_tools.html
        change_list_results.html
        delete_confirmation.html
        delete_selected_confirmation.html
        object_history.html
        login.html
        pagination.html
        search_form.html
        actions.html
        filter.html
        submit_line.html
        date_hierarchy.html
        includes/
          fieldset.html
          object_delete_summary.html
        auth/
          user/
            add_form.html
            change_password.html
        edit_inline/
          stacked.html
          tabular.html
      boost/
        components/
          navbar.html
          breadcrumbs.html
          pagination.html
          theme_toggle.html
          messages.html
        widgets/
          base.html
          skeleton.html
          value.html
          table.html
          chart.html
          recent_actions.html
        forms/
          field.html
          fieldset.html
    jinja2_env.py
    static/
      boost/
        css/
          boost.css
        js/
          alpine.js
          htmx.js
          chart.js
          boost.js
```

## Layout

Modern Compact layout:
- Top `navbar` with branding, user menu, theme toggle
- `breadcrumbs` below navbar
- Full-width content area
- Dashboard widgets on index page (no fixed sidebar)

## DaisyUI Component Mapping

| Admin Element | DaisyUI Component |
|---|---|
| Top nav | `navbar` + `dropdown` |
| Breadcrumbs | `breadcrumbs` |
| Change list table | `table` (clean minimal — subtle dividers, uppercase headers) |
| Pagination | `join` + `btn` group |
| Filters | `collapse` or `dropdown` |
| Search | `input` + `btn` in `form-control` |
| Actions bar | `select` + `btn` |
| Change form fieldsets | `card` + `card-body` |
| Form fields | `input`, `select`, `textarea`, `toggle`, `checkbox` |
| Inlines | `card` + `table` |
| Messages | `alert` (info/success/warning/error) |
| Delete confirmation | `card` + `btn btn-error` |
| Login | Centered `card` + `form-control` |
| Dashboard widgets | `card` + `card-body`, `skeleton` for HTMX |
| Theme toggle | `dropdown` with theme list |
| Badges/status | `badge` with color variants |

## Dashboard Widget System

```python
class Widget:
    template_name = "boost/widgets/base.html"
    htmx = False

    def get_context(self, request):
        raise NotImplementedError

class ValueWidget(Widget):
    """Single KPI value."""
    template_name = "boost/widgets/value.html"

class TableWidget(Widget):
    """Small data table."""
    template_name = "boost/widgets/table.html"

class ChartWidget(Widget):
    """Chart.js chart. htmx=True by default (lazy loaded)."""
    template_name = "boost/widgets/chart.html"
    htmx = True

class RecentActionsWidget(Widget):
    """Optional replacement for Django's recent actions sidebar."""
    template_name = "boost/widgets/recent_actions.html"
```

Usage:

```python
class MyAdminSite(AdminSite):
    dashboard_widgets = [
        [ValueWidget(...), ValueWidget(...), ValueWidget(...)],  # Row 1
        [RecentActionsWidget()],                                  # Row 2
    ]
```

Nested lists represent rows. HTMX widgets render a DaisyUI `skeleton` placeholder, then `hx-get` fetches real content from a widget endpoint on AdminSite.

ChartWidget provides a convenience wrapper using Chart.js, but users can subclass Widget with any chart library by providing their own template.

## Theming

- Light and dark as curated defaults
- All DaisyUI themes work via `data-theme` attribute on `<html>`
- Theme toggle uses Alpine.js, persists choice to `localStorage`
- No custom theme configuration needed — DaisyUI handles it

## Configuration

Minimal — stays close to stock Django admin:
- AdminSite attributes (site_header, site_title, index_title)
- ModelAdmin options (list_display, list_filter, search_fields, etc.)
- `dashboard_widgets` on AdminSite for the dashboard
- No UNFOLD-style settings dict

## Usage

```python
# settings.py
INSTALLED_APPS = [
    "django_admin_boost.boost",
    ...
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "APP_DIRS": True,
        "OPTIONS": {
            "environment": "django_admin_boost.boost.jinja2_env.environment",
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        ...
    },
]

# admin.py
from django_admin_boost.boost import ModelAdmin, register

@register(MyModel)
class MyModelAdmin(ModelAdmin):
    list_display = ["name", "status", "created"]
```

## Testing Strategy

Tests written from scratch (not ported from unfold).

1. **Template rendering** — each core template renders without errors with realistic context
2. **Admin view integration** — test client hits change list, change form, add, delete, history, login; verify status codes, correct templates, expected content
3. **Dashboard widgets** — widget get_context() returns expected data, HTMX endpoints respond, skeleton renders
4. **Widget unit tests** — ValueWidget, TableWidget, ChartWidget, RecentActionsWidget render correctly
5. **Theme** — theme toggle works, data-theme attribute set
6. **Existing tests** — 105 existing mixin/paginator tests keep passing

Test infrastructure: use existing `tests/testapp/` models, add `tests/boostapp/` admin configuration.

## Implementation Steps

1. Copy unfold Python files, strip theme/settings system, rewrite imports
2. Create dashboard.py with widget base classes
3. Build and ship pre-compiled DaisyUI + Tailwind CSS
4. Write Jinja2 templates from scratch for all core admin views
5. Create jinja2_env.py with all needed globals/filters
6. Write boost.js (theme persistence, select-all, glue)
7. Update pyproject.toml (ruff/mypy excludes, build config)
8. Write tests
9. Verify all admin views render and function correctly
