# Boost Admin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `django_admin_boost.boost` — a custom Django admin UI with Jinja2-native templates, DaisyUI components, and a dashboard widget system with HTMX lazy loading.

**Architecture:** Python layer based on the existing `django_admin_boost.admin` package (which already has Django's ModelAdmin with performance mixins). Templates written from scratch using DaisyUI semantic classes. Dashboard widget system as a first-class module. Alpine.js for interactivity, HTMX for lazy loading.

**Tech Stack:** Django 5.2+, Jinja2, DaisyUI 4.x, Tailwind CSS, Alpine.js, HTMX, Chart.js (optional)

---

## File Map

### New Files (boost package)

| File | Responsibility |
|---|---|
| `django_admin_boost/boost/__init__.py` | Public API re-exports |
| `django_admin_boost/boost/apps.py` | Django AppConfig |
| `django_admin_boost/boost/admin.py` | ModelAdmin, StackedInline, TabularInline |
| `django_admin_boost/boost/sites.py` | BoostAdminSite with dashboard widget support |
| `django_admin_boost/boost/dashboard.py` | Widget base classes (Widget, ValueWidget, TableWidget, ChartWidget, RecentActionsWidget) |
| `django_admin_boost/boost/decorators.py` | @register, @action, @display re-exports |
| `django_admin_boost/boost/jinja2_env.py` | Jinja2 environment factory with all globals/filters |
| `django_admin_boost/boost/jinja2/admin/base.html` | Base template — navbar, breadcrumbs, messages, content block |
| `django_admin_boost/boost/jinja2/admin/base_site.html` | Site wrapper extending base |
| `django_admin_boost/boost/jinja2/admin/index.html` | Dashboard with widget grid |
| `django_admin_boost/boost/jinja2/admin/app_index.html` | App model list |
| `django_admin_boost/boost/jinja2/admin/change_list.html` | Change list with table, filters, search, actions, pagination |
| `django_admin_boost/boost/jinja2/admin/change_form.html` | Change form with fieldsets |
| `django_admin_boost/boost/jinja2/admin/delete_confirmation.html` | Delete confirmation |
| `django_admin_boost/boost/jinja2/admin/delete_selected_confirmation.html` | Bulk delete confirmation |
| `django_admin_boost/boost/jinja2/admin/object_history.html` | Object history log |
| `django_admin_boost/boost/jinja2/admin/login.html` | Login page |
| `django_admin_boost/boost/jinja2/admin/actions.html` | Actions bar partial |
| `django_admin_boost/boost/jinja2/admin/pagination.html` | Pagination partial |
| `django_admin_boost/boost/jinja2/admin/search_form.html` | Search partial |
| `django_admin_boost/boost/jinja2/admin/filter.html` | Filter partial |
| `django_admin_boost/boost/jinja2/admin/submit_line.html` | Form submit buttons |
| `django_admin_boost/boost/jinja2/admin/change_list_results.html` | Table results partial |
| `django_admin_boost/boost/jinja2/admin/includes/fieldset.html` | Fieldset partial |
| `django_admin_boost/boost/jinja2/admin/edit_inline/stacked.html` | Stacked inline |
| `django_admin_boost/boost/jinja2/admin/edit_inline/tabular.html` | Tabular inline |
| `django_admin_boost/boost/jinja2/boost/components/navbar.html` | Top navigation bar |
| `django_admin_boost/boost/jinja2/boost/components/breadcrumbs.html` | Breadcrumb trail |
| `django_admin_boost/boost/jinja2/boost/components/messages.html` | Alert messages |
| `django_admin_boost/boost/jinja2/boost/components/theme_toggle.html` | Theme switcher dropdown |
| `django_admin_boost/boost/jinja2/boost/widgets/base.html` | Widget card wrapper |
| `django_admin_boost/boost/jinja2/boost/widgets/skeleton.html` | HTMX loading skeleton |
| `django_admin_boost/boost/jinja2/boost/widgets/value.html` | KPI value widget |
| `django_admin_boost/boost/jinja2/boost/widgets/table.html` | Table widget |
| `django_admin_boost/boost/jinja2/boost/widgets/chart.html` | Chart.js widget |
| `django_admin_boost/boost/jinja2/boost/widgets/recent_actions.html` | Recent actions widget |
| `django_admin_boost/boost/static/boost/css/boost.css` | Pre-compiled DaisyUI + Tailwind |
| `django_admin_boost/boost/static/boost/js/alpine.min.js` | Alpine.js |
| `django_admin_boost/boost/static/boost/js/htmx.min.js` | HTMX |
| `django_admin_boost/boost/static/boost/js/chart.min.js` | Chart.js (optional) |
| `django_admin_boost/boost/static/boost/js/boost.js` | Theme persistence + glue |

### New Test Files

| File | Responsibility |
|---|---|
| `tests/settings/boost.py` | Test settings using boost admin |
| `tests/settings/boost_urls.py` | URL conf for boost admin |
| `tests/boostapp/__init__.py` | Test app package |
| `tests/boostapp/admin.py` | Register testapp models with boost admin |
| `tests/test_boost_views.py` | Admin view integration tests |
| `tests/test_boost_dashboard.py` | Dashboard widget tests |
| `tests/test_boost_templates.py` | Template rendering tests |

### Modified Files

| File | Change |
|---|---|
| `pyproject.toml` | Add ruff/mypy excludes for copied boost files, add build includes |

---

## Task 1: Package Skeleton and AppConfig

**Files:**
- Create: `django_admin_boost/boost/__init__.py`
- Create: `django_admin_boost/boost/apps.py`
- Create: `django_admin_boost/boost/decorators.py`
- Create: `tests/settings/boost.py`
- Create: `tests/settings/boost_urls.py`
- Create: `tests/boostapp/__init__.py`
- Create: `tests/boostapp/admin.py`
- Test: `tests/test_boost_views.py`

- [ ] **Step 1: Create boost package with AppConfig**

Create `django_admin_boost/boost/__init__.py`:
```python
"""django-admin-boost custom admin UI.

Drop-in admin replacement with DaisyUI components and Jinja2 templates.

Usage::

    INSTALLED_APPS = ["django_admin_boost.boost", ...]

    # in your admin.py:
    from django_admin_boost.boost import ModelAdmin, register

    @register(MyModel)
    class MyModelAdmin(ModelAdmin):
        ...
"""

from django.utils.module_loading import autodiscover_modules

from django_admin_boost.admin.decorators import action, display, register
from django_admin_boost.admin.filters import (
    AllValuesFieldListFilter,
    BooleanFieldListFilter,
    ChoicesFieldListFilter,
    DateFieldListFilter,
    EmptyFieldListFilter,
    FieldListFilter,
    ListFilter,
    RelatedFieldListFilter,
    RelatedOnlyFieldListFilter,
    SimpleListFilter,
)
from django_admin_boost.admin.options import (
    HORIZONTAL,
    VERTICAL,
    ModelAdmin,
    ShowFacets,
    StackedInline,
    TabularInline,
)
from django_admin_boost.boost.sites import BoostAdminSite

site = BoostAdminSite()

# Re-export standalone mixins for convenience
from django_admin_boost.mixins import ListFieldsMixin, SmartPaginatorMixin
from django_admin_boost.paginators import EstimatedCountPaginator

__all__ = [
    "HORIZONTAL",
    "VERTICAL",
    "AllValuesFieldListFilter",
    "BoostAdminSite",
    "BooleanFieldListFilter",
    "ChoicesFieldListFilter",
    "DateFieldListFilter",
    "EmptyFieldListFilter",
    "EstimatedCountPaginator",
    "FieldListFilter",
    "ListFieldsMixin",
    "ListFilter",
    "ModelAdmin",
    "RelatedFieldListFilter",
    "RelatedOnlyFieldListFilter",
    "ShowFacets",
    "SimpleListFilter",
    "SmartPaginatorMixin",
    "StackedInline",
    "TabularInline",
    "action",
    "autodiscover",
    "display",
    "register",
    "site",
]


def autodiscover() -> None:
    autodiscover_modules("admin", register_to=site)
```

Create `django_admin_boost/boost/apps.py`:
```python
from django.apps import AppConfig


class BoostAdminConfig(AppConfig):
    name = "django_admin_boost.boost"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        self.module.autodiscover()
```

- [ ] **Step 2: Create BoostAdminSite**

Create `django_admin_boost/boost/sites.py`:
```python
"""Boost admin site with dashboard widget support."""

from django.contrib.admin import AdminSite
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse


class BoostAdminSite(AdminSite):
    """Admin site with dashboard widget grid on the index page."""

    # Dashboard widget rows — list of lists of Widget instances
    dashboard_widgets: list[list] = []

    def index(self, request: HttpRequest, extra_context: dict | None = None) -> HttpResponse:
        extra_context = extra_context or {}
        extra_context["dashboard_widgets"] = self._get_dashboard_widgets(request)
        return super().index(request, extra_context=extra_context)

    def _get_dashboard_widgets(self, request: HttpRequest) -> list[list[dict]]:
        """Resolve widget rows into context dicts for rendering."""
        rows = []
        for row in self.dashboard_widgets:
            rendered_row = []
            for widget in row:
                rendered_row.append({
                    "template_name": widget.template_name,
                    "htmx": widget.htmx,
                    "context": widget.get_context(request) if not widget.htmx else {},
                    "widget_id": id(widget),
                })
            rows.append(rendered_row)
        return rows

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path(
                "boost/widget/<int:widget_id>/",
                self.admin_view(self.widget_view),
                name="boost_widget",
            ),
        ]
        return custom_urls + urls

    def widget_view(self, request: HttpRequest, widget_id: int) -> HttpResponse:
        """HTMX endpoint for lazy-loaded dashboard widgets."""
        for row in self.dashboard_widgets:
            for widget in row:
                if id(widget) == widget_id:
                    context = widget.get_context(request)
                    return TemplateResponse(request, widget.template_name, context)
        return HttpResponse(status=404)
```

- [ ] **Step 3: Create test settings and boostapp**

Create `tests/settings/boost.py`:
```python
from tests.settings.base import *  # noqa: F403

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django_admin_boost.boost",
    "django.contrib.sessions",
    "django.contrib.messages",
    "tests.testapp",
]

ROOT_URLCONF = "tests.settings.boost_urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "environment": "django_admin_boost.boost.jinja2_env.environment",
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

Create `tests/settings/boost_urls.py`:
```python
from django.urls import path

from django_admin_boost.boost import site

urlpatterns = [
    path("admin/", site.urls),
]
```

Create `tests/boostapp/__init__.py` (empty).

Create `tests/boostapp/admin.py`:
```python
from django_admin_boost.boost import ModelAdmin, register

from tests.testapp.models import Article, Category


@register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@register(Article)
class ArticleAdmin(ModelAdmin):
    list_display = ["title", "category", "status", "is_featured", "priority", "publish_date", "created_at"]
    list_display_links = ["title"]
    list_filter = ["status", "is_featured", "category"]
    search_fields = ["title", "slug", "body"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at"]
    fieldsets = [
        (None, {"fields": ["title", "slug", "body", "category"]}),
        ("Publishing", {"fields": ["status", "is_featured", "priority", "publish_date"]}),
        ("Metadata", {"fields": ["created_at"], "classes": ["collapse"]}),
    ]
```

- [ ] **Step 4: Write smoke test for boost admin loading**

Create `tests/test_boost_views.py`:
```python
from django.contrib.auth.models import User
from django.test import TestCase, override_settings


@override_settings(ROOT_URLCONF="tests.settings.boost_urls")
class BoostAdminSmokeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser("admin", "admin@test.com", "password")

    def setUp(self):
        self.client.force_login(self.admin_user)

    def test_admin_index_loads(self):
        response = self.client.get("/admin/")
        assert response.status_code == 200
```

- [ ] **Step 5: Run test to verify it fails**

Run: `uv run pytest tests/test_boost_views.py -v --no-cov -p no:xdist`
Expected: FAIL (jinja2_env module doesn't exist yet, or templates missing)

- [ ] **Step 6: Commit skeleton**

```bash
git add django_admin_boost/boost/ tests/settings/boost.py tests/settings/boost_urls.py tests/boostapp/ tests/test_boost_views.py
git commit -m "feat(boost): package skeleton with AppConfig and BoostAdminSite"
```

---

## Task 2: Dashboard Widget System

**Files:**
- Create: `django_admin_boost/boost/dashboard.py`
- Test: `tests/test_boost_dashboard.py`

- [ ] **Step 1: Write failing tests for widget classes**

Create `tests/test_boost_dashboard.py`:
```python
from django.test import RequestFactory, TestCase

from django_admin_boost.boost.dashboard import (
    ChartWidget,
    RecentActionsWidget,
    TableWidget,
    ValueWidget,
    Widget,
)


class WidgetBaseTest(TestCase):
    def test_widget_has_template_and_htmx_attrs(self):
        w = Widget()
        assert hasattr(w, "template_name")
        assert hasattr(w, "htmx")
        assert w.htmx is False

    def test_widget_get_context_raises(self):
        w = Widget()
        factory = RequestFactory()
        request = factory.get("/admin/")
        with self.assertRaises(NotImplementedError):
            w.get_context(request)


class ValueWidgetTest(TestCase):
    def test_value_widget_context(self):
        w = ValueWidget(label="Total Users", value=1234, icon="people")
        factory = RequestFactory()
        request = factory.get("/admin/")
        ctx = w.get_context(request)
        assert ctx["label"] == "Total Users"
        assert ctx["value"] == 1234
        assert ctx["icon"] == "people"

    def test_value_widget_callable_value(self):
        w = ValueWidget(label="Count", value=lambda request: 42)
        factory = RequestFactory()
        request = factory.get("/admin/")
        ctx = w.get_context(request)
        assert ctx["value"] == 42


class TableWidgetTest(TestCase):
    def test_table_widget_context(self):
        w = TableWidget(
            title="Recent Orders",
            headers=["ID", "Customer", "Total"],
            rows=lambda request: [["1", "Alice", "$100"], ["2", "Bob", "$200"]],
        )
        factory = RequestFactory()
        request = factory.get("/admin/")
        ctx = w.get_context(request)
        assert ctx["title"] == "Recent Orders"
        assert ctx["headers"] == ["ID", "Customer", "Total"]
        assert len(ctx["rows"]) == 2


class ChartWidgetTest(TestCase):
    def test_chart_widget_is_htmx_by_default(self):
        w = ChartWidget(
            title="Sales",
            chart_type="bar",
            data=lambda request: {"labels": ["Jan"], "datasets": [{"data": [10]}]},
        )
        assert w.htmx is True

    def test_chart_widget_context(self):
        w = ChartWidget(
            title="Sales",
            chart_type="bar",
            data=lambda request: {"labels": ["Jan"], "datasets": [{"data": [10]}]},
        )
        factory = RequestFactory()
        request = factory.get("/admin/")
        ctx = w.get_context(request)
        assert ctx["title"] == "Sales"
        assert ctx["chart_type"] == "bar"
        assert "labels" in ctx["data"]


class RecentActionsWidgetTest(TestCase):
    def test_recent_actions_widget_context(self):
        w = RecentActionsWidget(limit=5)
        factory = RequestFactory()
        request = factory.get("/admin/")
        request.user = type("User", (), {"is_anonymous": True, "pk": None})()
        ctx = w.get_context(request)
        assert "entries" in ctx
        assert ctx["limit"] == 5
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_boost_dashboard.py -v --no-cov -p no:xdist`
Expected: FAIL (module doesn't exist)

- [ ] **Step 3: Implement dashboard.py**

Create `django_admin_boost/boost/dashboard.py`:
```python
"""Dashboard widget system for the boost admin index page."""

from __future__ import annotations

from typing import Any

from django.http import HttpRequest


class Widget:
    """Base dashboard widget. Subclass and override get_context()."""

    template_name: str = "boost/widgets/base.html"
    htmx: bool = False

    def get_context(self, request: HttpRequest) -> dict[str, Any]:
        raise NotImplementedError


class ValueWidget(Widget):
    """Single KPI value — e.g. 'Total Users: 1,234'."""

    template_name = "boost/widgets/value.html"

    def __init__(
        self,
        label: str,
        value: Any,
        icon: str = "",
        description: str = "",
        **kwargs: Any,
    ) -> None:
        self.label = label
        self._value = value
        self.icon = icon
        self.description = description
        self.htmx = kwargs.get("htmx", False)

    def get_context(self, request: HttpRequest) -> dict[str, Any]:
        value = self._value(request) if callable(self._value) else self._value
        return {
            "label": self.label,
            "value": value,
            "icon": self.icon,
            "description": self.description,
        }


class TableWidget(Widget):
    """Small data table — e.g. recent orders."""

    template_name = "boost/widgets/table.html"

    def __init__(
        self,
        title: str,
        headers: list[str],
        rows: Any,
        **kwargs: Any,
    ) -> None:
        self.title = title
        self.headers = headers
        self._rows = rows
        self.htmx = kwargs.get("htmx", False)

    def get_context(self, request: HttpRequest) -> dict[str, Any]:
        rows = self._rows(request) if callable(self._rows) else self._rows
        return {
            "title": self.title,
            "headers": self.headers,
            "rows": rows,
        }


class ChartWidget(Widget):
    """Chart.js chart. Lazy-loaded via HTMX by default."""

    template_name = "boost/widgets/chart.html"
    htmx = True

    def __init__(
        self,
        title: str,
        chart_type: str,
        data: Any,
        **kwargs: Any,
    ) -> None:
        self.title = title
        self.chart_type = chart_type
        self._data = data
        self.htmx = kwargs.get("htmx", True)

    def get_context(self, request: HttpRequest) -> dict[str, Any]:
        data = self._data(request) if callable(self._data) else self._data
        return {
            "title": self.title,
            "chart_type": self.chart_type,
            "data": data,
        }


class RecentActionsWidget(Widget):
    """Drop-in replacement for Django's recent actions sidebar."""

    template_name = "boost/widgets/recent_actions.html"

    def __init__(self, limit: int = 10, **kwargs: Any) -> None:
        self.limit = limit
        self.htmx = kwargs.get("htmx", False)

    def get_context(self, request: HttpRequest) -> dict[str, Any]:
        from django.contrib.admin.models import LogEntry

        qs = LogEntry.objects.select_related("content_type", "user")
        if not getattr(request.user, "is_anonymous", True):
            qs = qs.filter(user=request.user)
        return {
            "entries": list(qs[: self.limit]),
            "limit": self.limit,
        }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_boost_dashboard.py -v --no-cov -p no:xdist`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add django_admin_boost/boost/dashboard.py tests/test_boost_dashboard.py
git commit -m "feat(boost): dashboard widget system"
```

---

## Task 3: Jinja2 Environment

**Files:**
- Create: `django_admin_boost/boost/jinja2_env.py`

- [ ] **Step 1: Create Jinja2 environment factory**

Create `django_admin_boost/boost/jinja2_env.py`:
```python
"""Jinja2 environment factory for boost admin templates."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from urllib.parse import quote

import jinja2
from django.templatetags.static import static
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.dateformat import format as dateformat
from django.utils.encoding import iri_to_uri
from django.utils.formats import date_format, localize
from django.utils.html import conditional_escape
from django.utils.text import Truncator, capfirst
from django.utils.translation import get_language, get_language_bidi, gettext, ngettext
from markupsafe import Markup

from django_admin_boost.admin.models import LogEntry
from django_admin_boost.admin.templatetags.admin_list import (
    admin_actions as _raw_admin_actions,
)
from django_admin_boost.admin.templatetags.admin_list import (
    admin_list_filter as _raw_admin_list_filter,
)
from django_admin_boost.admin.templatetags.admin_list import (
    date_hierarchy,
    pagination,
    paginator_number,
    result_headers,
    result_hidden_fields,
    result_list,
    results,
    search_form,
)
from django_admin_boost.admin.templatetags.admin_modify import (
    cell_count,
)
from django_admin_boost.admin.templatetags.admin_modify import (
    prepopulated_fields_js as _raw_prepopulated_fields_js,
)
from django_admin_boost.admin.templatetags.admin_modify import (
    submit_row as _raw_submit_row,
)
from django_admin_boost.admin.templatetags.admin_urls import (
    add_preserved_filters as _raw_add_preserved_filters,
)


def environment(**options: object) -> jinja2.Environment:
    """Create a Jinja2 environment configured for boost admin templates.

    Usage in settings::

        TEMPLATES = [{
            "BACKEND": "django.template.backends.jinja2.Jinja2",
            "APP_DIRS": True,
            "OPTIONS": {
                "environment": "django_admin_boost.boost.jinja2_env.environment",
            },
        }]
    """
    env = jinja2.Environment(**options)  # type: ignore[arg-type]  # noqa: S701
    env.add_extension("jinja2.ext.i18n")

    env.install_gettext_callables(gettext, ngettext, newstyle=True)  # type: ignore[attr-defined]

    env.globals.update(
        {
            "get_current_language": get_language,
            "get_current_language_bidi": get_language_bidi,
            "get_admin_log": _get_admin_log,
            "now": _now,
            "static": static,
            "url": _url,
            # Admin list/modify/url helpers
            "admin_actions": _admin_actions_jinja2,
            "admin_list_filter": _admin_list_filter_safe,
            "date_hierarchy": date_hierarchy,
            "pagination": pagination,
            "paginator_number": paginator_number,
            "result_headers": result_headers,
            "result_hidden_fields": result_hidden_fields,
            "result_list": result_list,
            "results": results,
            "search_form": search_form,
            "prepopulated_fields_js": _prepopulated_fields_js_jinja2,
            "submit_row": _submit_row_jinja2,
            "add_preserved_filters": _add_preserved_filters_jinja2,
        },
    )

    env.filters.update(
        {
            "admin_urlname": _admin_urlname,
            "admin_urlquote": _admin_urlquote,
            "capfirst": _capfirst_safe,
            "iriencode": _iriencode,
            "cell_count": cell_count,
            "date": _date_filter,
            "truncatewords": _truncatewords,
            "unlocalize": _unlocalize,
            "unordered_list": _unordered_list,
            "urlencode_path": _urlencode_path,
            "yesno": _yesno,
        },
    )

    return env


# --- Globals ---

@jinja2.pass_context
def _url(context: Any, viewname: str, *args: object, silent: bool = False, **kwargs: object) -> str:
    try:
        request = context.get("request") if context else None
        current_app = getattr(request, "current_app", None) if request else None
        return reverse(viewname, args=args, kwargs=kwargs, current_app=current_app)
    except NoReverseMatch:
        if silent:
            return ""
        raise


def _now(format_string: str) -> str:
    return dateformat(datetime.now(tz=timezone.get_current_timezone()), format_string)


def _get_admin_log(limit: int = 10, user: object = None) -> object:
    qs = LogEntry.objects.select_related("content_type", "user")
    if user is not None and not getattr(user, "is_anonymous", True):
        qs = qs.filter(user=user)  # type: ignore[misc]
    return qs[:limit]


# --- Filters ---

def _yesno(value: object, arg: str = "yes,no,maybe") -> str:
    bits = arg.split(",")
    if len(bits) < 2:
        return str(value)
    yes, no = bits[0], bits[1]
    maybe = bits[2] if len(bits) > 2 else bits[1]
    if value is None:
        return maybe
    return yes if value else no


def _admin_urlname(value: Any, arg: str) -> str:
    return "admin:%s_%s_%s" % (value.app_label, value.model_name, arg)


def _admin_urlquote(value: object) -> str:
    return quote(str(value))


def _capfirst_safe(value: object) -> str | Markup:
    result = capfirst(str(value)) if value else ""
    if hasattr(value, "__html__"):
        return Markup(result)
    return result


def _iriencode(value: str) -> str:
    return iri_to_uri(value)


def _admin_list_filter_safe(cl: Any, spec: Any) -> Markup:
    return Markup(_raw_admin_list_filter(cl, spec))


def _jinja2_context_to_dict(context: Any) -> dict[str, Any]:
    if isinstance(context, dict):
        return context
    return dict(context)


@jinja2.pass_context
def _admin_actions_jinja2(context: Any) -> dict[str, Any]:
    return _raw_admin_actions(_jinja2_context_to_dict(context))


@jinja2.pass_context
def _submit_row_jinja2(context: Any) -> dict[str, Any]:
    return _raw_submit_row(_jinja2_context_to_dict(context))


@jinja2.pass_context
def _prepopulated_fields_js_jinja2(context: Any) -> dict[str, Any]:
    return _raw_prepopulated_fields_js(_jinja2_context_to_dict(context))


@jinja2.pass_context
def _add_preserved_filters_jinja2(
    context: Any,
    url: str,
    popup: bool = False,
    to_field: str | None = None,
) -> str:
    return _raw_add_preserved_filters(_jinja2_context_to_dict(context), url, popup, to_field)


def _urlencode_path(value: str) -> str:
    return quote(str(value), safe="/")


def _date_filter(value: Any, arg: str = "DATETIME_FORMAT") -> str:
    if value in (None, ""):
        return ""
    try:
        return date_format(value, arg)
    except AttributeError:
        return ""


def _truncatewords(value: str, arg: int | str = 15) -> str:
    try:
        length = int(arg)
    except (ValueError, TypeError):
        return str(value)
    return Truncator(value).words(length, truncate=" \u2026")


def _unlocalize(value: Any) -> str:
    return str(localize(value, use_l10n=False))


def _unordered_list(value: list[Any]) -> str:
    def _helper(items: list[Any]) -> list[str]:
        output: list[str] = []
        for item in items:
            if isinstance(item, (list, tuple)):
                if output:
                    last = output.pop()
                    last = last.removesuffix("</li>")
                    output.append(last)
                    output.append("<ul>")
                    output.extend(_helper(list(item)))
                    output.append("</ul>")
                    output.append("</li>")
                else:
                    output.append("<ul>")
                    output.extend(_helper(list(item)))
                    output.append("</ul>")
            else:
                output.append(f"<li>{conditional_escape(item)}</li>")
        return output
    return Markup("\n".join(_helper(value)))
```

- [ ] **Step 2: Verify import works**

Run: `uv run python -c "from django_admin_boost.boost.jinja2_env import environment; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add django_admin_boost/boost/jinja2_env.py
git commit -m "feat(boost): Jinja2 environment factory"
```

---

## Task 4: Static Assets (CSS + JS)

**Files:**
- Create: `django_admin_boost/boost/static/boost/css/boost.css`
- Create: `django_admin_boost/boost/static/boost/js/alpine.min.js`
- Create: `django_admin_boost/boost/static/boost/js/htmx.min.js`
- Create: `django_admin_boost/boost/static/boost/js/chart.min.js`
- Create: `django_admin_boost/boost/static/boost/js/boost.js`

- [ ] **Step 1: Download DaisyUI + Tailwind pre-built CSS**

Use the DaisyUI CDN build as a starting point. Download and save:
```bash
curl -o django_admin_boost/boost/static/boost/css/boost.css "https://cdn.jsdelivr.net/npm/daisyui@4/dist/full.min.css"
```

Prepend the Tailwind base to it (or use a standalone Tailwind CLI build with DaisyUI plugin if available).

- [ ] **Step 2: Download Alpine.js, HTMX, Chart.js**

```bash
curl -o django_admin_boost/boost/static/boost/js/alpine.min.js "https://cdn.jsdelivr.net/npm/alpinejs@3/dist/cdn.min.js"
curl -o django_admin_boost/boost/static/boost/js/htmx.min.js "https://cdn.jsdelivr.net/npm/htmx.org@2/dist/htmx.min.js"
curl -o django_admin_boost/boost/static/boost/js/chart.min.js "https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"
```

- [ ] **Step 3: Create boost.js glue script**

Create `django_admin_boost/boost/static/boost/js/boost.js`:
```javascript
/* Boost Admin — theme persistence and UI glue */
document.addEventListener('alpine:init', () => {
    Alpine.store('theme', {
        current: localStorage.getItem('boost-theme') || 'light',
        set(name) {
            this.current = name;
            document.documentElement.setAttribute('data-theme', name);
            localStorage.setItem('boost-theme', name);
        },
        init() {
            document.documentElement.setAttribute('data-theme', this.current);
        }
    });
});

/* Select-all checkbox for actions */
document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('action-toggle');
    if (toggle) {
        toggle.addEventListener('change', (e) => {
            document.querySelectorAll('input.action-select').forEach(cb => {
                cb.checked = e.target.checked;
            });
        });
    }
});
```

- [ ] **Step 4: Commit**

```bash
git add django_admin_boost/boost/static/
git commit -m "feat(boost): static assets — DaisyUI CSS, Alpine.js, HTMX, Chart.js, boost.js"
```

---

## Task 5: Base Templates (base.html, navbar, breadcrumbs, messages)

**Files:**
- Create: `django_admin_boost/boost/jinja2/admin/base.html`
- Create: `django_admin_boost/boost/jinja2/admin/base_site.html`
- Create: `django_admin_boost/boost/jinja2/boost/components/navbar.html`
- Create: `django_admin_boost/boost/jinja2/boost/components/breadcrumbs.html`
- Create: `django_admin_boost/boost/jinja2/boost/components/messages.html`
- Create: `django_admin_boost/boost/jinja2/boost/components/theme_toggle.html`

- [ ] **Step 1: Create base.html**

Create `django_admin_boost/boost/jinja2/admin/base.html`:
```html
<!DOCTYPE html>
<html lang="{{ get_current_language() }}" data-theme="light">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}{{ title }} | {{ site_title|default(gettext("Django site admin")) }}{% endblock %}</title>
    <link rel="stylesheet" href="{{ static('boost/css/boost.css') }}">
    {% block extrastyle %}{% endblock %}
    {% block extrahead %}{% endblock %}
</head>
<body class="bg-base-200 min-h-screen {% block bodyclass %}{% endblock %}" x-data>
    {% include "boost/components/navbar.html" %}
    <main class="container mx-auto px-4 py-6 max-w-7xl">
        {% include "boost/components/breadcrumbs.html" %}
        {% include "boost/components/messages.html" %}
        <div id="content" class="{% block coltype %}{% endblock %}">
            {% block content %}{% endblock %}
        </div>
    </main>
    {% block footer %}{% endblock %}
    <script src="{{ static('boost/js/alpine.min.js') }}" defer></script>
    <script src="{{ static('boost/js/htmx.min.js') }}"></script>
    <script src="{{ static('boost/js/boost.js') }}"></script>
    {% block extrajs %}{% endblock %}
</body>
</html>
```

- [ ] **Step 2: Create base_site.html**

Create `django_admin_boost/boost/jinja2/admin/base_site.html`:
```html
{% extends "admin/base.html" %}

{% block title %}{% if subtitle %}{{ subtitle }} | {% endif %}{{ title }} | {{ site_title|default(gettext("Django site admin")) }}{% endblock %}

{% block nav_global %}{% endblock %}
```

- [ ] **Step 3: Create navbar component**

Create `django_admin_boost/boost/jinja2/boost/components/navbar.html`:
```html
<div class="navbar bg-base-100 shadow-sm">
    <div class="container mx-auto max-w-7xl">
        <div class="flex-1">
            <a href="{{ url('admin:index') }}" class="btn btn-ghost text-xl">
                {{ site_header|default(gettext("Django administration")) }}
            </a>
        </div>
        <div class="flex-none gap-2">
            {% include "boost/components/theme_toggle.html" %}
            {% if user.is_active and user.is_staff %}
            <div class="dropdown dropdown-end">
                <div tabindex="0" role="button" class="btn btn-ghost btn-circle avatar placeholder">
                    <div class="bg-neutral text-neutral-content w-10 rounded-full">
                        <span>{{ user.get_short_name()[:2]|upper if user.get_short_name() else user.get_username()[:2]|upper }}</span>
                    </div>
                </div>
                <ul tabindex="0" class="dropdown-content menu bg-base-100 rounded-box z-[1] w-52 p-2 shadow">
                    {% if user.has_usable_password() %}
                    <li><a href="{{ url('admin:password_change') }}">{{ gettext("Change password") }}</a></li>
                    {% endif %}
                    <li><a href="{{ url('admin:logout') }}">{{ gettext("Log out") }}</a></li>
                </ul>
            </div>
            {% endif %}
        </div>
    </div>
</div>
```

- [ ] **Step 4: Create breadcrumbs component**

Create `django_admin_boost/boost/jinja2/boost/components/breadcrumbs.html`:
```html
{% if breadcrumbs %}
<div class="breadcrumbs text-sm mb-4">
    <ul>
        <li><a href="{{ url('admin:index') }}">{{ gettext("Home") }}</a></li>
        {% for crumb in breadcrumbs %}
            {% if crumb.url %}
                <li><a href="{{ crumb.url }}">{{ crumb.name }}</a></li>
            {% else %}
                <li>{{ crumb.name }}</li>
            {% endif %}
        {% endfor %}
    </ul>
</div>
{% endif %}
```

- [ ] **Step 5: Create messages component**

Create `django_admin_boost/boost/jinja2/boost/components/messages.html`:
```html
{% if messages %}
{% for message in messages %}
<div class="alert alert-{{ 'success' if message.tags == 'success' else 'info' if message.tags == 'info' else 'warning' if message.tags == 'warning' else 'error' if message.tags == 'error' else 'info' }} mb-4">
    <span>{{ message }}</span>
</div>
{% endfor %}
{% endif %}
```

- [ ] **Step 6: Create theme toggle component**

Create `django_admin_boost/boost/jinja2/boost/components/theme_toggle.html`:
```html
<div class="dropdown dropdown-end" x-data>
    <div tabindex="0" role="button" class="btn btn-ghost btn-sm gap-1">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
        </svg>
        <span class="text-xs" x-text="$store.theme.current"></span>
    </div>
    <ul tabindex="0" class="dropdown-content menu bg-base-100 rounded-box z-[1] w-40 p-2 shadow">
        <li><a @click="$store.theme.set('light')">Light</a></li>
        <li><a @click="$store.theme.set('dark')">Dark</a></li>
        <li><a @click="$store.theme.set('cupcake')">Cupcake</a></li>
        <li><a @click="$store.theme.set('corporate')">Corporate</a></li>
        <li><a @click="$store.theme.set('nord')">Nord</a></li>
    </ul>
</div>
```

- [ ] **Step 7: Commit**

```bash
git add django_admin_boost/boost/jinja2/
git commit -m "feat(boost): base templates — layout, navbar, breadcrumbs, messages, theme toggle"
```

---

## Task 6: Login Template

**Files:**
- Create: `django_admin_boost/boost/jinja2/admin/login.html`

- [ ] **Step 1: Create login.html**

Create `django_admin_boost/boost/jinja2/admin/login.html`:
```html
{% extends "admin/base_site.html" %}

{% block bodyclass %}login{% endblock %}

{% block content %}
<div class="flex items-center justify-center min-h-[60vh]">
    <div class="card bg-base-100 shadow-xl w-full max-w-md">
        <div class="card-body">
            <h2 class="card-title text-2xl mb-4">{{ site_header|default(gettext("Django administration")) }}</h2>
            {% if form.errors %}
            <div class="alert alert-error mb-4">
                <span>{{ gettext("Please enter the correct username and password for a staff account.") }}</span>
            </div>
            {% endif %}
            <form method="post" action="{{ app_path }}">
                {{ csrf_input }}
                <div class="form-control mb-4">
                    <label class="label" for="id_username">
                        <span class="label-text">{{ gettext("Username:") }}</span>
                    </label>
                    <input type="text" name="username" id="id_username" class="input input-bordered w-full" autofocus required>
                </div>
                <div class="form-control mb-6">
                    <label class="label" for="id_password">
                        <span class="label-text">{{ gettext("Password:") }}</span>
                    </label>
                    <input type="password" name="password" id="id_password" class="input input-bordered w-full" required>
                </div>
                <input type="hidden" name="next" value="{{ next }}">
                <div class="card-actions justify-end">
                    <button type="submit" class="btn btn-primary w-full">{{ gettext("Log in") }}</button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 2: Commit**

```bash
git add django_admin_boost/boost/jinja2/admin/login.html
git commit -m "feat(boost): login template"
```

---

## Task 7: Index (Dashboard) Template + Widget Templates

**Files:**
- Create: `django_admin_boost/boost/jinja2/admin/index.html`
- Create: `django_admin_boost/boost/jinja2/admin/app_index.html`
- Create: `django_admin_boost/boost/jinja2/boost/widgets/base.html`
- Create: `django_admin_boost/boost/jinja2/boost/widgets/skeleton.html`
- Create: `django_admin_boost/boost/jinja2/boost/widgets/value.html`
- Create: `django_admin_boost/boost/jinja2/boost/widgets/table.html`
- Create: `django_admin_boost/boost/jinja2/boost/widgets/chart.html`
- Create: `django_admin_boost/boost/jinja2/boost/widgets/recent_actions.html`

- [ ] **Step 1: Create index.html (dashboard)**

Create `django_admin_boost/boost/jinja2/admin/index.html`:
```html
{% extends "admin/base_site.html" %}

{% block title %}{{ site_title }}{% endblock %}

{% block content %}
{% if dashboard_widgets %}
<div class="mb-8">
    {% for row in dashboard_widgets %}
    <div class="grid grid-cols-1 md:grid-cols-{{ row|length }} gap-4 mb-4">
        {% for widget in row %}
            {% if widget.htmx %}
                {% include "boost/widgets/skeleton.html" %}
            {% else %}
                {% include widget.template_name %}
            {% endif %}
        {% endfor %}
    </div>
    {% endfor %}
</div>
{% endif %}

<h2 class="text-2xl font-bold mb-4">{{ gettext("Site administration") }}</h2>

{% if app_list %}
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {% for app in app_list %}
    <div class="card bg-base-100 shadow-sm">
        <div class="card-body">
            <h3 class="card-title">
                <a href="{{ app.app_url }}" class="link link-hover">{{ app.name }}</a>
            </h3>
            <table class="table table-sm">
                <tbody>
                {% for model in app.models %}
                    <tr>
                        <td>
                            {% if model.admin_url %}
                                <a href="{{ model.admin_url }}" class="link">{{ model.name }}</a>
                            {% else %}
                                {{ model.name }}
                            {% endif %}
                        </td>
                        <td class="text-right">
                            {% if model.add_url %}
                                <a href="{{ model.add_url }}" class="btn btn-xs btn-ghost">{{ gettext("Add") }}</a>
                            {% endif %}
                            {% if model.admin_url %}
                                <a href="{{ model.admin_url }}" class="btn btn-xs btn-ghost">{{ gettext("Change") }}</a>
                            {% endif %}
                        </td>
                    </tr>
                {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endfor %}
</div>
{% else %}
<p>{{ gettext("You don't have permission to view or edit anything.") }}</p>
{% endif %}
{% endblock %}
```

- [ ] **Step 2: Create app_index.html**

Create `django_admin_boost/boost/jinja2/admin/app_index.html`:
```html
{% extends "admin/base_site.html" %}

{% block title %}{{ app_label }} | {{ site_title }}{% endblock %}

{% block content %}
<h2 class="text-2xl font-bold mb-4">{{ title }}</h2>

{% if app_list %}
<div class="grid grid-cols-1 gap-4">
    {% for app in app_list %}
    <div class="card bg-base-100 shadow-sm">
        <div class="card-body">
            <table class="table">
                <tbody>
                {% for model in app.models %}
                    <tr>
                        <td>
                            {% if model.admin_url %}
                                <a href="{{ model.admin_url }}" class="link">{{ model.name }}</a>
                            {% else %}
                                {{ model.name }}
                            {% endif %}
                        </td>
                        <td class="text-right">
                            {% if model.add_url %}
                                <a href="{{ model.add_url }}" class="btn btn-xs btn-ghost">{{ gettext("Add") }}</a>
                            {% endif %}
                            {% if model.admin_url %}
                                <a href="{{ model.admin_url }}" class="btn btn-xs btn-ghost">{{ gettext("Change") }}</a>
                            {% endif %}
                        </td>
                    </tr>
                {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endfor %}
</div>
{% endif %}
{% endblock %}
```

- [ ] **Step 3: Create widget templates**

Create `django_admin_boost/boost/jinja2/boost/widgets/base.html`:
```html
<div class="card bg-base-100 shadow-sm">
    <div class="card-body">
        {% block widget_content %}{% endblock %}
    </div>
</div>
```

Create `django_admin_boost/boost/jinja2/boost/widgets/skeleton.html`:
```html
<div class="card bg-base-100 shadow-sm"
     hx-get="{{ url('admin:boost_widget', widget.widget_id) }}"
     hx-trigger="load"
     hx-swap="outerHTML">
    <div class="card-body">
        <div class="skeleton h-4 w-1/3 mb-2"></div>
        <div class="skeleton h-8 w-1/2 mb-4"></div>
        <div class="skeleton h-4 w-full"></div>
    </div>
</div>
```

Create `django_admin_boost/boost/jinja2/boost/widgets/value.html`:
```html
<div class="card bg-base-100 shadow-sm">
    <div class="card-body">
        <p class="text-sm text-base-content/60">{{ widget.context.label }}</p>
        <p class="text-3xl font-bold">{{ widget.context.value }}</p>
        {% if widget.context.description %}
        <p class="text-sm text-base-content/60">{{ widget.context.description }}</p>
        {% endif %}
    </div>
</div>
```

Create `django_admin_boost/boost/jinja2/boost/widgets/table.html`:
```html
<div class="card bg-base-100 shadow-sm">
    <div class="card-body">
        <h3 class="card-title text-lg">{{ widget.context.title }}</h3>
        <table class="table table-sm">
            <thead>
                <tr>
                {% for header in widget.context.headers %}
                    <th class="text-xs uppercase tracking-wider text-base-content/60">{{ header }}</th>
                {% endfor %}
                </tr>
            </thead>
            <tbody>
                {% for row in widget.context.rows %}
                <tr>
                    {% for cell in row %}
                    <td>{{ cell }}</td>
                    {% endfor %}
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
```

Create `django_admin_boost/boost/jinja2/boost/widgets/chart.html`:
```html
<div class="card bg-base-100 shadow-sm">
    <div class="card-body">
        <h3 class="card-title text-lg">{{ title }}</h3>
        <canvas id="chart-{{ widget_id }}" width="400" height="200"></canvas>
        <script src="{{ static('boost/js/chart.min.js') }}"></script>
        <script>
            new Chart(document.getElementById('chart-{{ widget_id }}'), {
                type: '{{ chart_type }}',
                data: {{ data|tojson }},
            });
        </script>
    </div>
</div>
```

Create `django_admin_boost/boost/jinja2/boost/widgets/recent_actions.html`:
```html
<div class="card bg-base-100 shadow-sm">
    <div class="card-body">
        <h3 class="card-title text-lg">{{ gettext("Recent actions") }}</h3>
        {% if widget.context.entries %}
        <table class="table table-sm">
            <tbody>
                {% for entry in widget.context.entries %}
                <tr>
                    <td>{{ entry.action_time|date("SHORT_DATETIME_FORMAT") }}</td>
                    <td>
                        {% if entry.content_type %}
                            {{ entry.content_type.name|capfirst }}
                        {% endif %}
                    </td>
                    <td>{{ entry.object_repr }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p class="text-sm text-base-content/60">{{ gettext("None available") }}</p>
        {% endif %}
    </div>
</div>
```

- [ ] **Step 4: Commit**

```bash
git add django_admin_boost/boost/jinja2/admin/index.html django_admin_boost/boost/jinja2/admin/app_index.html django_admin_boost/boost/jinja2/boost/widgets/
git commit -m "feat(boost): index/dashboard and widget templates"
```

---

## Task 8: Change List Template

**Files:**
- Create: `django_admin_boost/boost/jinja2/admin/change_list.html`
- Create: `django_admin_boost/boost/jinja2/admin/change_list_results.html`
- Create: `django_admin_boost/boost/jinja2/admin/actions.html`
- Create: `django_admin_boost/boost/jinja2/admin/search_form.html`
- Create: `django_admin_boost/boost/jinja2/admin/filter.html`
- Create: `django_admin_boost/boost/jinja2/admin/pagination.html`
- Create: `django_admin_boost/boost/jinja2/admin/date_hierarchy.html`

- [ ] **Step 1: Create change_list.html**

Create `django_admin_boost/boost/jinja2/admin/change_list.html`:
```html
{% extends "admin/base_site.html" %}

{% block extrastyle %}
    {{ super() }}
    <script src="{{ url('admin:jsi18n') }}"></script>
    {{ media.css }}
{% endblock %}

{% block extrahead %}
    {{ super() }}
    {{ media.js }}
{% endblock %}

{% block bodyclass %}{{ super() }} app-{{ opts.app_label }} model-{{ opts.model_name }} change-list{% endblock %}

{% block content %}
<div id="content-main">
    {% if cl.formset and cl.formset.errors %}
    <div class="alert alert-error mb-4">
        <span>{{ cl.formset.errors }}</span>
    </div>
    {{ cl.formset.non_form_errors() }}
    {% endif %}

    <div id="changelist" class="{% if cl.has_filters %}filtered{% endif %}">
        {% block search %}
            {% include "admin/search_form.html" %}
        {% endblock %}

        {% block date_hierarchy %}
            {% if cl.date_hierarchy %}
                {% include "admin/date_hierarchy.html" %}
            {% endif %}
        {% endblock %}

        <form id="changelist-form" method="post">
            {{ csrf_input }}
            {% if cl.formset %}
                {{ cl.formset.management_form }}
            {% endif %}

            {% block result_list %}
                {% include "admin/actions.html" %}
                {% include "admin/change_list_results.html" %}
            {% endblock %}

            {% block pagination %}
                {% include "admin/pagination.html" %}
            {% endblock %}
        </form>

        {% if cl.has_filters %}
        <div class="mt-4">
            <div class="collapse collapse-arrow bg-base-100 shadow-sm">
                <input type="checkbox" />
                <div class="collapse-title font-medium">{{ gettext("Filter") }}</div>
                <div class="collapse-content">
                    {% for spec in cl.filter_specs %}
                        {% include "admin/filter.html" %}
                    {% endfor %}
                </div>
            </div>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}
```

- [ ] **Step 2: Create remaining change list partials**

Create `django_admin_boost/boost/jinja2/admin/change_list_results.html`:
```html
{% set result_headers_list = result_headers(cl)|list %}
{% set results_list = results(cl)|list %}

{% if results_list %}
<div class="overflow-x-auto">
    <table class="table">
        <thead>
            <tr>
                {% for header in result_headers_list %}
                <th class="text-xs uppercase tracking-wider text-base-content/60 {{ header.class_attrib }}">
                    {% if header.sortable %}
                        <a href="{{ header.url_primary }}">{{ header.text }}</a>
                        {% if header.sorted %}
                            <span class="text-xs">{{ "▲" if header.ascending else "▼" }}</span>
                        {% endif %}
                    {% else %}
                        {{ header.text }}
                    {% endif %}
                </th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for result in results_list %}
            <tr class="hover">
                {% for item in result %}
                    {{ item }}
                {% endfor %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% else %}
<div class="alert alert-info">
    <span>{{ cl.get_empty_value_display() if cl.get_empty_value_display else gettext("0 results") }}</span>
</div>
{% endif %}

{% for field in result_hidden_fields(cl) %}
    {{ field }}
{% endfor %}
```

Create `django_admin_boost/boost/jinja2/admin/actions.html`:
```html
{% if action_form and actions_on_top %}
<div class="flex items-center gap-2 mb-4">
    <select name="action" class="select select-bordered select-sm">
        <option value="" selected>{{ gettext("---------") }}</option>
        {% for action in action_form.fields.action.choices %}
            {% if action.0 %}
            <option value="{{ action.0 }}">{{ action.1 }}</option>
            {% endif %}
        {% endfor %}
    </select>
    <button type="submit" name="index" value="0" class="btn btn-sm btn-primary">{{ gettext("Go") }}</button>
    {% if cl.result_count != cl.full_result_count %}
    <span class="text-sm text-base-content/60">
        {{ cl.result_count }} {{ gettext("of") }} {{ cl.full_result_count }}
    </span>
    {% else %}
    <span class="text-sm text-base-content/60">
        {{ cl.result_count }} {{ cl.opts.verbose_name_plural }}
    </span>
    {% endif %}
</div>
{% endif %}
```

Create `django_admin_boost/boost/jinja2/admin/search_form.html`:
```html
{% if cl.search_fields %}
<div class="mb-4">
    <form id="changelist-search" method="get">
        <div class="join">
            <input type="text" name="{{ search_var }}" value="{{ cl.query }}" class="input input-bordered join-item" placeholder="{{ gettext('Search') }}">
            <button type="submit" class="btn btn-primary join-item">{{ gettext("Search") }}</button>
            {% if cl.query %}
            <a href="{{ cl.get_query_string(remove=[search_var]) }}" class="btn btn-ghost join-item">{{ gettext("Clear") }}</a>
            {% endif %}
        </div>
    </form>
</div>
{% endif %}
```

Create `django_admin_boost/boost/jinja2/admin/filter.html`:
```html
<div class="mb-2">
    <h4 class="font-semibold text-sm mb-1">{{ spec.title }}</h4>
    <ul class="menu menu-sm bg-base-200 rounded-box">
        {% for choice in spec.choices(cl) %}
        <li>
            <a href="{{ choice.query_string }}" class="{{ 'active' if choice.selected else '' }}">
                {{ choice.display }}
            </a>
        </li>
        {% endfor %}
    </ul>
</div>
```

Create `django_admin_boost/boost/jinja2/admin/pagination.html`:
```html
{% if cl.paginator.num_pages > 1 %}
<div class="flex justify-center mt-4">
    <div class="join">
        {% for i in cl.paginator.get_elided_page_range(cl.page_num) %}
            {% if i == cl.page_num %}
                <button class="join-item btn btn-sm btn-active">{{ i }}</button>
            {% elif i == '…' %}
                <button class="join-item btn btn-sm btn-disabled">…</button>
            {% else %}
                <a href="{{ cl.get_query_string({page_var: i}) }}" class="join-item btn btn-sm">{{ i }}</a>
            {% endif %}
        {% endfor %}
    </div>
</div>
{% endif %}
```

Create `django_admin_boost/boost/jinja2/admin/date_hierarchy.html`:
```html
{% set date_hierarchy_ctx = date_hierarchy(cl) %}
{% if date_hierarchy_ctx %}
<div class="mb-4">
    <div class="flex flex-wrap gap-1">
        {% if date_hierarchy_ctx.back %}
            <a href="{{ date_hierarchy_ctx.back.link }}" class="btn btn-xs btn-ghost">« {{ gettext("Back") }}</a>
        {% endif %}
        {% for choice in date_hierarchy_ctx.choices %}
            <a href="{{ choice.link }}" class="btn btn-xs {{ 'btn-primary' if choice.selected else 'btn-ghost' }}">{{ choice.title }}</a>
        {% endfor %}
    </div>
</div>
{% endif %}
```

- [ ] **Step 3: Commit**

```bash
git add django_admin_boost/boost/jinja2/admin/change_list.html django_admin_boost/boost/jinja2/admin/change_list_results.html django_admin_boost/boost/jinja2/admin/actions.html django_admin_boost/boost/jinja2/admin/search_form.html django_admin_boost/boost/jinja2/admin/filter.html django_admin_boost/boost/jinja2/admin/pagination.html django_admin_boost/boost/jinja2/admin/date_hierarchy.html
git commit -m "feat(boost): change list template with search, filters, actions, pagination"
```

---

## Task 9: Change Form + Fieldset + Submit + Inline Templates

**Files:**
- Create: `django_admin_boost/boost/jinja2/admin/change_form.html`
- Create: `django_admin_boost/boost/jinja2/admin/submit_line.html`
- Create: `django_admin_boost/boost/jinja2/admin/includes/fieldset.html`
- Create: `django_admin_boost/boost/jinja2/admin/edit_inline/stacked.html`
- Create: `django_admin_boost/boost/jinja2/admin/edit_inline/tabular.html`

- [ ] **Step 1: Create change_form.html**

Create `django_admin_boost/boost/jinja2/admin/change_form.html`:
```html
{% extends "admin/base_site.html" %}

{% block extrastyle %}
    {{ super() }}
    <script src="{{ url('admin:jsi18n') }}"></script>
    {{ media.css }}
{% endblock %}

{% block extrahead %}
    {{ super() }}
    {{ media.js }}
{% endblock %}

{% block bodyclass %}{{ super() }} app-{{ opts.app_label }} model-{{ opts.model_name }} change-form{% endblock %}

{% block content %}
<form method="post" id="{{ opts.model_name }}_form" enctype="multipart/form-data" novalidate>
    {{ csrf_input }}

    {% if is_popup %}<input type="hidden" name="_popup" value="1">{% endif %}
    {% if to_field %}<input type="hidden" name="_to_field" value="{{ to_field }}">{% endif %}

    {% if errors %}
    <div class="alert alert-error mb-4">
        <div>
            <p class="font-bold">{{ gettext("Please correct the errors below.") }}</p>
            {{ adminform.form.non_field_errors() }}
        </div>
    </div>
    {% endif %}

    {% for fieldset in adminform %}
        {% include "admin/includes/fieldset.html" %}
    {% endfor %}

    {% for inline_admin_formset in inline_admin_formsets %}
        {% if inline_admin_formset.opts.template == "admin/edit_inline/stacked.html" or "stacked" in inline_admin_formset.opts.template %}
            {% include "admin/edit_inline/stacked.html" %}
        {% else %}
            {% include "admin/edit_inline/tabular.html" %}
        {% endif %}
    {% endfor %}

    {% include "admin/submit_line.html" %}
</form>
{% endblock %}
```

- [ ] **Step 2: Create submit_line.html**

Create `django_admin_boost/boost/jinja2/admin/submit_line.html`:
```html
{% set submit_ctx = submit_row() %}
<div class="flex justify-between items-center mt-6 pt-4 border-t border-base-300">
    <div>
        {% if submit_ctx.show_delete_link %}
            <a href="{{ url(opts|admin_urlname('delete'), original.pk|admin_urlquote) }}" class="btn btn-error btn-outline btn-sm">{{ gettext("Delete") }}</a>
        {% endif %}
    </div>
    <div class="flex gap-2">
        {% if submit_ctx.show_save_as_new %}
            <input type="submit" value="{{ gettext('Save as new') }}" name="_saveasnew" class="btn btn-sm btn-ghost">
        {% endif %}
        {% if submit_ctx.show_save_and_add_another %}
            <input type="submit" value="{{ gettext('Save and add another') }}" name="_addanother" class="btn btn-sm btn-ghost">
        {% endif %}
        {% if submit_ctx.show_save_and_continue %}
            <input type="submit" value="{{ gettext('Save and continue editing') }}" name="_continue" class="btn btn-sm btn-outline btn-primary">
        {% endif %}
        {% if submit_ctx.show_save %}
            <input type="submit" value="{{ gettext('Save') }}" name="_save" class="btn btn-sm btn-primary">
        {% endif %}
    </div>
</div>
```

- [ ] **Step 3: Create fieldset.html**

Create `django_admin_boost/boost/jinja2/admin/includes/fieldset.html`:
```html
<div class="card bg-base-100 shadow-sm mb-4 {{ 'collapse collapse-arrow' if 'collapse' in fieldset.classes else '' }}">
    {% if 'collapse' in fieldset.classes %}
    <input type="checkbox" />
    {% endif %}
    {% if fieldset.name %}
    <div class="{{ 'collapse-title' if 'collapse' in fieldset.classes else 'card-body pb-0' }}">
        <h3 class="font-semibold text-lg">{{ fieldset.name }}</h3>
    </div>
    {% endif %}
    <div class="{{ 'collapse-content' if 'collapse' in fieldset.classes else 'card-body' }}">
        {% for line in fieldset %}
        <div class="grid grid-cols-{{ line.fields|length }} gap-4 mb-4">
            {% for field in line %}
            <div class="form-control">
                {% if not field.is_readonly %}
                    {% if field.field.label %}
                    <label class="label" for="{{ field.field.auto_id }}">
                        <span class="label-text">{{ field.field.label }}{% if field.field.field.required %} *{% endif %}</span>
                    </label>
                    {% endif %}
                    {{ field.field }}
                    {% if field.field.help_text %}
                    <label class="label">
                        <span class="label-text-alt text-base-content/60">{{ field.field.help_text }}</span>
                    </label>
                    {% endif %}
                    {% if field.field.errors %}
                    {% for error in field.field.errors %}
                    <label class="label">
                        <span class="label-text-alt text-error">{{ error }}</span>
                    </label>
                    {% endfor %}
                    {% endif %}
                {% else %}
                    <label class="label">
                        <span class="label-text">{{ field.field.label }}</span>
                    </label>
                    <div class="py-2">{{ field.contents }}</div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endfor %}
    </div>
</div>
```

- [ ] **Step 4: Create inline templates**

Create `django_admin_boost/boost/jinja2/admin/edit_inline/stacked.html`:
```html
<div class="card bg-base-100 shadow-sm mb-4">
    <div class="card-body">
        <h3 class="card-title">{{ inline_admin_formset.opts.verbose_name_plural|capfirst }}</h3>
        {{ inline_admin_formset.formset.management_form }}
        {% for inline_admin_form in inline_admin_formset %}
        <div class="border border-base-300 rounded-lg p-4 mb-2 {{ 'opacity-50' if inline_admin_form.original and inline_admin_form.show_url else '' }}">
            {% if inline_admin_form.original %}
                <p class="font-semibold mb-2">{{ inline_admin_form.original }}</p>
            {% endif %}
            {% for fieldset in inline_admin_form %}
                {% for line in fieldset %}
                <div class="grid grid-cols-{{ line.fields|length }} gap-4 mb-2">
                    {% for field in line %}
                    <div class="form-control">
                        {% if field.field.label %}
                        <label class="label"><span class="label-text">{{ field.field.label }}</span></label>
                        {% endif %}
                        {{ field.field }}
                    </div>
                    {% endfor %}
                </div>
                {% endfor %}
            {% endfor %}
            {% if inline_admin_formset.formset.can_delete and inline_admin_form.original %}
                <label class="label cursor-pointer justify-start gap-2">
                    <input type="checkbox" name="{{ inline_admin_form.deletion_field.html_name }}" class="checkbox checkbox-error checkbox-sm">
                    <span class="label-text text-error">{{ gettext("Delete") }}</span>
                </label>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</div>
```

Create `django_admin_boost/boost/jinja2/admin/edit_inline/tabular.html`:
```html
<div class="card bg-base-100 shadow-sm mb-4">
    <div class="card-body">
        <h3 class="card-title">{{ inline_admin_formset.opts.verbose_name_plural|capfirst }}</h3>
        {{ inline_admin_formset.formset.management_form }}
        <div class="overflow-x-auto">
            <table class="table table-sm">
                <thead>
                    <tr>
                        {% for field in inline_admin_formset.fields() %}
                            {% if not field.widget.is_hidden %}
                            <th class="text-xs uppercase tracking-wider">{{ field.label|capfirst }}</th>
                            {% endif %}
                        {% endfor %}
                        {% if inline_admin_formset.formset.can_delete %}
                        <th class="text-xs uppercase tracking-wider">{{ gettext("Delete?") }}</th>
                        {% endif %}
                    </tr>
                </thead>
                <tbody>
                    {% for inline_admin_form in inline_admin_formset %}
                    <tr>
                        {% for fieldset in inline_admin_form %}
                            {% for line in fieldset %}
                                {% for field in line %}
                                    {% if not field.field.is_hidden %}
                                    <td>{{ field.field }}</td>
                                    {% endif %}
                                {% endfor %}
                            {% endfor %}
                        {% endfor %}
                        {% if inline_admin_formset.formset.can_delete and inline_admin_form.original %}
                        <td>
                            <input type="checkbox" name="{{ inline_admin_form.deletion_field.html_name }}" class="checkbox checkbox-error checkbox-sm">
                        </td>
                        {% endif %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
```

- [ ] **Step 5: Commit**

```bash
git add django_admin_boost/boost/jinja2/admin/change_form.html django_admin_boost/boost/jinja2/admin/submit_line.html django_admin_boost/boost/jinja2/admin/includes/ django_admin_boost/boost/jinja2/admin/edit_inline/
git commit -m "feat(boost): change form, fieldset, submit line, and inline templates"
```

---

## Task 10: Delete + History + Remaining Templates

**Files:**
- Create: `django_admin_boost/boost/jinja2/admin/delete_confirmation.html`
- Create: `django_admin_boost/boost/jinja2/admin/delete_selected_confirmation.html`
- Create: `django_admin_boost/boost/jinja2/admin/object_history.html`

- [ ] **Step 1: Create delete and history templates**

Create `django_admin_boost/boost/jinja2/admin/delete_confirmation.html`:
```html
{% extends "admin/base_site.html" %}

{% block content %}
<div class="card bg-base-100 shadow-sm max-w-2xl">
    <div class="card-body">
        <h2 class="card-title text-error">{{ gettext("Are you sure?") }}</h2>
        <p>{{ gettext("Are you sure you want to delete the %(object_name)s \"%(escaped_object)s\"? All of the following related items will be deleted:")|format(object_name=opts.verbose_name, escaped_object=object) }}</p>

        {% if deleted_objects %}
        <ul class="list-disc list-inside my-4">
            {% for obj in deleted_objects %}
            <li>{{ obj }}</li>
            {% endfor %}
        </ul>
        {% endif %}

        <form method="post">
            {{ csrf_input }}
            <input type="hidden" name="post" value="yes">
            <div class="card-actions justify-end mt-4">
                <a href="{{ object_url }}" class="btn btn-ghost">{{ gettext("No, take me back") }}</a>
                <button type="submit" class="btn btn-error">{{ gettext("Yes, I'm sure") }}</button>
            </div>
        </form>
    </div>
</div>
{% endblock %}
```

Create `django_admin_boost/boost/jinja2/admin/delete_selected_confirmation.html`:
```html
{% extends "admin/base_site.html" %}

{% block content %}
<div class="card bg-base-100 shadow-sm max-w-2xl">
    <div class="card-body">
        <h2 class="card-title text-error">{{ gettext("Are you sure?") }}</h2>
        <p>{{ gettext("Are you sure you want to delete the selected %(objects_name)s? All of the following objects and their related items will be deleted:")|format(objects_name=opts.verbose_name_plural) }}</p>

        {% if deletable_objects %}
        <ul class="list-disc list-inside my-4">
            {% for obj in deletable_objects %}
            <li>{{ obj }}</li>
            {% endfor %}
        </ul>
        {% endif %}

        <form method="post">
            {{ csrf_input }}
            {% for obj in queryset %}
            <input type="hidden" name="_selected_action" value="{{ obj.pk }}">
            {% endfor %}
            <input type="hidden" name="action" value="delete_selected">
            <input type="hidden" name="post" value="yes">
            <div class="card-actions justify-end mt-4">
                <button type="submit" name="cancel" class="btn btn-ghost">{{ gettext("No, take me back") }}</button>
                <button type="submit" class="btn btn-error">{{ gettext("Yes, I'm sure") }}</button>
            </div>
        </form>
    </div>
</div>
{% endblock %}
```

Create `django_admin_boost/boost/jinja2/admin/object_history.html`:
```html
{% extends "admin/base_site.html" %}

{% block content %}
<div class="card bg-base-100 shadow-sm">
    <div class="card-body">
        <h2 class="card-title">{{ gettext("Change history:") }} {{ object }}</h2>
        {% if action_list %}
        <table class="table">
            <thead>
                <tr>
                    <th class="text-xs uppercase tracking-wider text-base-content/60">{{ gettext("Date/time") }}</th>
                    <th class="text-xs uppercase tracking-wider text-base-content/60">{{ gettext("User") }}</th>
                    <th class="text-xs uppercase tracking-wider text-base-content/60">{{ gettext("Action") }}</th>
                </tr>
            </thead>
            <tbody>
                {% for action in action_list %}
                <tr>
                    <td>{{ action.action_time|date("DATETIME_FORMAT") }}</td>
                    <td>{{ action.user.get_username() }}</td>
                    <td>{{ action.get_change_message() }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p class="text-base-content/60">{{ gettext("This object doesn't have a change history.") }}</p>
        {% endif %}
    </div>
</div>
{% endblock %}
```

- [ ] **Step 2: Commit**

```bash
git add django_admin_boost/boost/jinja2/admin/delete_confirmation.html django_admin_boost/boost/jinja2/admin/delete_selected_confirmation.html django_admin_boost/boost/jinja2/admin/object_history.html
git commit -m "feat(boost): delete confirmation and object history templates"
```

---

## Task 11: Update pyproject.toml

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add ruff/mypy excludes for boost copied files and per-file ignores for jinja2_env**

Add to `extend-exclude` in `[tool.ruff]`:
```toml
  # boost jinja2_env has lazy imports by design
```

Add to `[tool.ruff.lint.per-file-ignores]`:
```toml
"django_admin_boost/boost/jinja2_env.py" = [
  "ANN",
  "ARG",
  "FBT",
  "PLC0415",
  "RUF012",
  "SIM110",
]
```

- [ ] **Step 2: Commit**

```bash
git add pyproject.toml
git commit -m "build: add boost ruff/mypy configuration"
```

---

## Task 12: Integration Tests

**Files:**
- Modify: `tests/test_boost_views.py`

- [ ] **Step 1: Write integration tests for all major admin views**

Update `tests/test_boost_views.py`:
```python
from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from tests.testapp.models import Article, Category

BOOST_SETTINGS = {
    "ROOT_URLCONF": "tests.settings.boost_urls",
    "INSTALLED_APPS": [
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django_admin_boost.boost",
        "django.contrib.sessions",
        "django.contrib.messages",
        "tests.testapp",
    ],
    "TEMPLATES": [
        {
            "BACKEND": "django.template.backends.jinja2.Jinja2",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "environment": "django_admin_boost.boost.jinja2_env.environment",
                "context_processors": [
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ],
}


@override_settings(**BOOST_SETTINGS)
class BoostAdminViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser("admin", "admin@test.com", "password")
        cls.category = Category.objects.create(name="Tech")
        cls.article = Article.objects.create(
            title="Test Article",
            slug="test-article",
            body="Test body",
            category=cls.category,
            status=Article.Status.PUBLISHED,
        )

    def setUp(self):
        self.client.force_login(self.admin_user)

    def test_index(self):
        response = self.client.get("/admin/")
        assert response.status_code == 200

    def test_app_index(self):
        response = self.client.get("/admin/testapp/")
        assert response.status_code == 200

    def test_change_list(self):
        response = self.client.get("/admin/testapp/article/")
        assert response.status_code == 200

    def test_add_form(self):
        response = self.client.get("/admin/testapp/article/add/")
        assert response.status_code == 200

    def test_change_form(self):
        response = self.client.get(f"/admin/testapp/article/{self.article.pk}/change/")
        assert response.status_code == 200

    def test_delete_confirmation(self):
        response = self.client.get(f"/admin/testapp/article/{self.article.pk}/delete/")
        assert response.status_code == 200

    def test_object_history(self):
        response = self.client.get(f"/admin/testapp/article/{self.article.pk}/history/")
        assert response.status_code == 200

    def test_login_page(self):
        self.client.logout()
        response = self.client.get("/admin/login/")
        assert response.status_code == 200


@override_settings(**BOOST_SETTINGS)
class BoostAdminSearchFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser("admin", "admin@test.com", "password")
        for i in range(25):
            Article.objects.create(title=f"Article {i}", status=Article.Status.PUBLISHED if i % 2 else Article.Status.DRAFT)

    def setUp(self):
        self.client.force_login(self.admin_user)

    def test_search(self):
        response = self.client.get("/admin/testapp/article/?q=Article+1")
        assert response.status_code == 200

    def test_filter(self):
        response = self.client.get("/admin/testapp/article/?status__exact=published")
        assert response.status_code == 200
```

- [ ] **Step 2: Run all tests**

Run: `uv run pytest tests/test_boost_views.py tests/test_boost_dashboard.py -v --no-cov -p no:xdist`
Expected: All PASS

- [ ] **Step 3: Run full test suite to check for regressions**

Run: `uv run pytest -x --no-cov`
Expected: All 105+ tests PASS

- [ ] **Step 4: Commit**

```bash
git add tests/
git commit -m "test(boost): integration tests for all admin views"
```

---

## Task 13: Final Verification

- [ ] **Step 1: Run full test suite**

Run: `uv run pytest -x -q --no-cov`
Expected: All tests pass, including original 105 + new boost tests

- [ ] **Step 2: Run linters**

Run: `uv run ruff check && uv run ruff format --check`
Expected: No errors

- [ ] **Step 3: Verify boost admin imports cleanly**

Run:
```bash
uv run python -c "
from django_admin_boost.boost import ModelAdmin, BoostAdminSite, site, register
from django_admin_boost.boost.dashboard import ValueWidget, TableWidget, ChartWidget, RecentActionsWidget
from django_admin_boost.boost.jinja2_env import environment
print('All imports OK')
print(f'Widgets: {ValueWidget.__name__}, {TableWidget.__name__}, {ChartWidget.__name__}, {RecentActionsWidget.__name__}')
"
```
Expected: All imports succeed

- [ ] **Step 4: Final commit and push**

```bash
git push -u origin feat/boost
```
