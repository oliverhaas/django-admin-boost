# Admin Contrib Modules Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port advanced filters, non-related inlines, and custom widgets from `unfold.contrib` to the standard admin as three optional Django apps.

**Architecture:** Direct port from `django_admin_boost.unfold.contrib`, replacing unfold-specific widgets with Django stock admin widgets, restyling Tailwind templates to Django admin CSS, and self-containing utilities. Each contrib module is a standalone Django app registered via `INSTALLED_APPS`.

**Tech Stack:** Django 5.2+, Jinja2, nouislider (slider filter), Trix (WYSIWYG), Alpine.js (array widget)

**Spec:** `docs/superpowers/specs/2026-04-06-admin-contrib-design.md`

**Source reference:** All unfold contrib code lives on the `feat/unfold` branch. Use `git show feat/unfold:<path>` to read source files.

---

## File Map

### New files to create

```
django_admin_boost/admin/contrib/
├── __init__.py
├── filters/
│   ├── __init__.py
│   ├── apps.py
│   ├── utils.py
│   ├── forms.py
│   ├── admin/
│   │   ├── __init__.py
│   │   ├── mixins.py
│   │   ├── text_filters.py
│   │   ├── choice_filters.py
│   │   ├── datetime_filters.py
│   │   ├── numeric_filters.py
│   │   ├── dropdown_filters.py
│   │   └── autocomplete_filters.py
│   ├── jinja2/admin/filters/
│   │   ├── filters_field.html
│   │   ├── filters_numeric_range.html
│   │   ├── filters_numeric_single.html
│   │   ├── filters_numeric_slider.html
│   │   ├── filters_date_range.html
│   │   └── filters_datetime_range.html
│   ├── templates/admin/filters/
│   │   └── (same 6 files as jinja2, in DTL syntax)
│   └── static/admin/contrib/filters/
│       ├── css/nouislider/nouislider.min.css
│       ├── css/nouislider/LICENSE
│       ├── js/nouislider/nouislider.min.js
│       ├── js/nouislider/LICENSE
│       ├── js/wnumb/wNumb.min.js
│       ├── js/wnumb/LICENSE
│       ├── js/admin-numeric-filter.js
│       ├── js/DateTimeShortcuts.js
│       └── js/select2.init.js
├── inlines/
│   ├── __init__.py
│   ├── apps.py
│   ├── checks.py
│   ├── forms.py
│   └── admin.py
└── forms/
    ├── __init__.py
    ├── apps.py
    ├── widgets.py
    ├── jinja2/admin/forms/
    │   ├── array.html
    │   ├── wysiwyg.html
    │   └── helpers/toolbar.html
    ├── templates/admin/forms/
    │   └── (same 3 files in DTL syntax)
    └── static/admin/contrib/forms/
        ├── css/trix/trix.css
        ├── css/trix/LICENSE
        ├── js/trix/trix.js
        ├── js/trix/LICENSE
        ├── js/trix.config.js
        └── js/alpine.min.js
```

### Files to modify

```
tests/settings/base.py         — add contrib apps to INSTALLED_APPS
```

### Test files to create

```
tests/test_contrib_filters.py
tests/test_contrib_inlines.py
tests/test_contrib_forms.py
```

---

## Task 1: Scaffold contrib directory and apps

Create the directory structure, `__init__.py` files, and `apps.py` for each contrib module. Update test settings.

**Files:**
- Create: `django_admin_boost/admin/contrib/__init__.py`
- Create: `django_admin_boost/admin/contrib/filters/__init__.py`
- Create: `django_admin_boost/admin/contrib/filters/apps.py`
- Create: `django_admin_boost/admin/contrib/inlines/__init__.py`
- Create: `django_admin_boost/admin/contrib/inlines/apps.py`
- Create: `django_admin_boost/admin/contrib/forms/__init__.py`
- Create: `django_admin_boost/admin/contrib/forms/apps.py`
- Modify: `tests/settings/base.py`

- [ ] **Step 1: Create contrib package and apps**

`django_admin_boost/admin/contrib/__init__.py` — empty file.

`django_admin_boost/admin/contrib/filters/__init__.py` — empty file.

`django_admin_boost/admin/contrib/filters/apps.py`:
```python
from django.apps import AppConfig


class DefaultAppConfig(AppConfig):
    name = "django_admin_boost.admin.contrib.filters"
    label = "boost_filters"
```

`django_admin_boost/admin/contrib/inlines/__init__.py` — empty file.

`django_admin_boost/admin/contrib/inlines/apps.py`:
```python
from django.apps import AppConfig


class DefaultAppConfig(AppConfig):
    name = "django_admin_boost.admin.contrib.inlines"
    label = "boost_inlines"
```

`django_admin_boost/admin/contrib/forms/__init__.py` — empty file.

`django_admin_boost/admin/contrib/forms/apps.py`:
```python
from django.apps import AppConfig


class DefaultAppConfig(AppConfig):
    name = "django_admin_boost.admin.contrib.forms"
    label = "boost_forms"
```

- [ ] **Step 2: Update test settings**

In `tests/settings/base.py`, add the three contrib apps to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django_admin_boost.admin",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django_admin_boost.admin.contrib.filters",
    "django_admin_boost.admin.contrib.inlines",
    "django_admin_boost.admin.contrib.forms",
    "tests.testapp",
]
```

- [ ] **Step 3: Verify apps load**

Run: `python -m pytest --co -q 2>&1 | head -20`
Expected: test collection succeeds (no import errors)

- [ ] **Step 4: Commit**

```bash
git add django_admin_boost/admin/contrib/ tests/settings/base.py
git commit -m "feat(contrib): scaffold contrib directory with three app configs

refs #16"
```

---

## Task 2: Filters — utilities and forms

Port the date/datetime parsing utilities and all filter form classes.

**Files:**
- Create: `django_admin_boost/admin/contrib/filters/utils.py`
- Create: `django_admin_boost/admin/contrib/filters/forms.py`
- Create: `tests/test_contrib_filters.py`

- [ ] **Step 1: Write tests for utils**

Create `tests/test_contrib_filters.py`:

```python
import datetime

from django.test import TestCase, override_settings


class ParseDateStrTest(TestCase):
    def test_parses_iso_format(self) -> None:
        from django_admin_boost.admin.contrib.filters.utils import parse_date_str

        result = parse_date_str("2026-01-15")
        assert result == datetime.date(2026, 1, 15)

    def test_returns_none_for_invalid(self) -> None:
        from django_admin_boost.admin.contrib.filters.utils import parse_date_str

        result = parse_date_str("not-a-date")
        assert result is None

    @override_settings(DATE_INPUT_FORMATS=["%d/%m/%Y", "%Y-%m-%d"])
    def test_uses_settings_formats(self) -> None:
        from django_admin_boost.admin.contrib.filters.utils import parse_date_str

        result = parse_date_str("15/01/2026")
        assert result == datetime.date(2026, 1, 15)


class ParseDateTimeStrTest(TestCase):
    def test_parses_iso_format(self) -> None:
        from django_admin_boost.admin.contrib.filters.utils import parse_datetime_str

        result = parse_datetime_str("2026-01-15 10:30:00")
        assert result == datetime.datetime(2026, 1, 15, 10, 30, 0)

    def test_returns_none_for_invalid(self) -> None:
        from django_admin_boost.admin.contrib.filters.utils import parse_datetime_str

        result = parse_datetime_str("not-a-datetime")
        assert result is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_contrib_filters.py -v --no-cov 2>&1 | tail -10`
Expected: FAIL — `ImportError: cannot import name 'parse_date_str'`

- [ ] **Step 3: Implement utils.py**

Create `django_admin_boost/admin/contrib/filters/utils.py`:

```python
from __future__ import annotations

import datetime

from django.conf import settings


def parse_date_str(value: str) -> datetime.date | None:
    """Parse a date string using Django's DATE_INPUT_FORMATS."""
    for fmt in settings.DATE_INPUT_FORMATS:
        try:
            return datetime.datetime.strptime(value, fmt).date()
        except (ValueError, TypeError):
            continue
    return None


def parse_datetime_str(value: str) -> datetime.datetime | None:
    """Parse a datetime string using Django's DATETIME_INPUT_FORMATS."""
    for fmt in settings.DATETIME_INPUT_FORMATS:
        try:
            return datetime.datetime.strptime(value, fmt)
        except (ValueError, TypeError):
            continue
    return None
```

- [ ] **Step 4: Run utils tests to verify they pass**

Run: `python -m pytest tests/test_contrib_filters.py -v --no-cov 2>&1 | tail -10`
Expected: 5 passed

- [ ] **Step 5: Write tests for filter forms**

Append to `tests/test_contrib_filters.py`:

```python
from django.contrib.admin.widgets import AdminRadioSelect, AdminSplitDateTime
from django.forms import CheckboxSelectMultiple, Select


class SearchFormTest(TestCase):
    def test_creates_text_field(self) -> None:
        from django_admin_boost.admin.contrib.filters.forms import SearchForm

        form = SearchForm(name="q", label="Search", data={"q": "test"})
        assert "q" in form.fields
        assert form.fields["q"].required is False


class CheckboxFormTest(TestCase):
    def test_creates_multiple_choice_field(self) -> None:
        from django_admin_boost.admin.contrib.filters.forms import CheckboxForm

        form = CheckboxForm(
            name="status",
            label="By status",
            choices=[("draft", "Draft"), ("published", "Published")],
            data={"status": ["draft"]},
        )
        assert "status" in form.fields
        assert isinstance(form.fields["status"].widget, CheckboxSelectMultiple)


class RadioFormTest(TestCase):
    def test_creates_choice_field(self) -> None:
        from django_admin_boost.admin.contrib.filters.forms import RadioForm

        form = RadioForm(
            name="status",
            label="By status",
            choices=[("", "All"), ("draft", "Draft")],
            data={"status": ""},
        )
        assert "status" in form.fields
        assert isinstance(form.fields["status"].widget, AdminRadioSelect)


class DropdownFormTest(TestCase):
    def test_creates_select_field(self) -> None:
        from django_admin_boost.admin.contrib.filters.forms import DropdownForm

        form = DropdownForm(
            name="category",
            label="By category",
            choices=[("", "All"), ("1", "News")],
            data={"category": ""},
        )
        assert "category" in form.fields
        assert isinstance(form.fields["category"].widget, Select)


class RangeNumericFormTest(TestCase):
    def test_creates_from_and_to_fields(self) -> None:
        from django_admin_boost.admin.contrib.filters.forms import RangeNumericForm

        form = RangeNumericForm(name="price", data={})
        assert "price_from" in form.fields
        assert "price_to" in form.fields


class SingleNumericFormTest(TestCase):
    def test_creates_numeric_field(self) -> None:
        from django_admin_boost.admin.contrib.filters.forms import SingleNumericForm

        form = SingleNumericForm(name="priority", data={})
        assert "priority" in form.fields


class RangeDateFormTest(TestCase):
    def test_creates_date_from_and_to(self) -> None:
        from django_admin_boost.admin.contrib.filters.forms import RangeDateForm

        form = RangeDateForm(name="publish_date", data={})
        assert "publish_date_from" in form.fields
        assert "publish_date_to" in form.fields


class RangeDateTimeFormTest(TestCase):
    def test_creates_datetime_from_and_to(self) -> None:
        from django_admin_boost.admin.contrib.filters.forms import RangeDateTimeForm

        form = RangeDateTimeForm(name="created_at", data={})
        assert "created_at_from" in form.fields
        assert "created_at_to" in form.fields
        assert isinstance(form.fields["created_at_from"].widget, AdminSplitDateTime)
```

- [ ] **Step 6: Run form tests to verify they fail**

Run: `python -m pytest tests/test_contrib_filters.py -v --no-cov -k "Form" 2>&1 | tail -15`
Expected: FAIL — `ImportError: cannot import name 'SearchForm'`

- [ ] **Step 7: Implement forms.py**

Create `django_admin_boost/admin/contrib/filters/forms.py`:

```python
from __future__ import annotations

from django import forms
from django.conf import settings
from django.contrib.admin.options import HORIZONTAL, ModelAdmin
from django.contrib.admin.widgets import (
    AdminRadioSelect,
    AdminSplitDateTime,
    AdminTextInputWidget,
    AutocompleteSelect,
    AutocompleteSelectMultiple,
)
from django.db.models import Field as ModelField
from django.forms import (
    CheckboxSelectMultiple,
    ChoiceField,
    ModelMultipleChoiceField,
    MultipleChoiceField,
    Select,
    SelectMultiple,
)
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _


class SearchForm(forms.Form):
    def __init__(self, name: str, label: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields[name] = forms.CharField(
            label=label,
            required=False,
            widget=AdminTextInputWidget,
        )


class AutocompleteDropdownForm(forms.Form):
    field = forms.ModelChoiceField
    widget = AutocompleteSelect

    def __init__(
        self,
        request: HttpRequest,
        name: str,
        label: str,
        choices: tuple,
        field: ModelField,
        model_admin: ModelAdmin,
        multiple: bool = False,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        if multiple:
            self.field = ModelMultipleChoiceField
            self.widget = AutocompleteSelectMultiple

        self.fields[name] = self.field(
            label=label,
            required=False,
            queryset=field.remote_field.model.objects,
            widget=self.widget(
                field,
                model_admin.admin_site,
            ),
        )

    class Media:
        extra = "" if settings.DEBUG else ".min"
        js = (
            f"admin/js/vendor/jquery/jquery{extra}.js",
            "admin/js/vendor/select2/select2.full.js",
            "admin/js/jquery.init.js",
            "admin/contrib/filters/js/select2.init.js",
        )
        css = {
            "screen": (
                "admin/css/vendor/select2/select2.css",
                "admin/css/autocomplete.css",
            ),
        }


class CheckboxForm(forms.Form):
    field = MultipleChoiceField
    widget = CheckboxSelectMultiple

    def __init__(
        self,
        name: str,
        label: str,
        choices: tuple | list,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.fields[name] = self.field(
            label=label,
            required=False,
            choices=choices,
            widget=self.widget,
        )


class RadioForm(CheckboxForm):
    field = ChoiceField
    widget = AdminRadioSelect


class HorizontalRadioForm(RadioForm):
    widget = AdminRadioSelect(radio_style=HORIZONTAL)


class DropdownForm(forms.Form):
    widget = Select
    field = ChoiceField

    def __init__(
        self,
        name: str,
        label: str,
        choices: tuple,
        multiple: bool = False,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        widget = self.widget
        field = self.field

        if multiple:
            widget = SelectMultiple
            field = MultipleChoiceField

        self.fields[name] = field(
            label=label,
            required=False,
            choices=choices,
            widget=widget,
        )

    class Media:
        extra = "" if settings.DEBUG else ".min"
        js = (
            f"admin/js/vendor/jquery/jquery{extra}.js",
            "admin/js/vendor/select2/select2.full.js",
            "admin/js/jquery.init.js",
            "admin/contrib/filters/js/select2.init.js",
        )
        css = {
            "screen": (
                "admin/css/vendor/select2/select2.css",
                "admin/css/autocomplete.css",
            ),
        }


class SingleNumericForm(forms.Form):
    def __init__(self, name: str, *args, **kwargs) -> None:
        self.name = name
        super().__init__(*args, **kwargs)

        self.fields[name] = forms.FloatField(
            label="",
            required=False,
            widget=forms.NumberInput(attrs={"placeholder": _("Value")}),
        )


class RangeNumericForm(forms.Form):
    def __init__(
        self,
        name: str,
        min: float | None = None,
        max: float | None = None,
        *args,
        **kwargs,
    ) -> None:
        self.name = name
        super().__init__(*args, **kwargs)

        min_max = {}
        if min:
            min_max["min"] = min
        if max:
            min_max["max"] = max

        self.fields[self.name + "_from"] = forms.FloatField(
            label="",
            required=False,
            widget=forms.NumberInput(attrs={"placeholder": _("From"), **min_max}),
        )
        self.fields[self.name + "_to"] = forms.FloatField(
            label="",
            required=False,
            widget=forms.NumberInput(attrs={"placeholder": _("To"), **min_max}),
        )


class SliderNumericForm(RangeNumericForm):
    class Media:
        css = {"all": ("admin/contrib/filters/css/nouislider/nouislider.min.css",)}
        js = (
            "admin/contrib/filters/js/wnumb/wNumb.min.js",
            "admin/contrib/filters/js/nouislider/nouislider.min.js",
            "admin/contrib/filters/js/admin-numeric-filter.js",
        )


class RangeDateForm(forms.Form):
    class Media:
        js = [
            "admin/js/calendar.js",
            "admin/contrib/filters/js/DateTimeShortcuts.js",
        ]

    def __init__(self, name: str, *args, **kwargs) -> None:
        self.name = name
        super().__init__(*args, **kwargs)

        self.fields[self.name + "_from"] = forms.DateField(
            label="",
            required=False,
            widget=forms.DateInput(
                attrs={"placeholder": _("From"), "class": "vCustomDateField"},
            ),
        )
        self.fields[self.name + "_to"] = forms.DateField(
            label="",
            required=False,
            widget=forms.DateInput(
                attrs={"placeholder": _("To"), "class": "vCustomDateField"},
            ),
        )


class RangeDateTimeForm(forms.Form):
    class Media:
        js = [
            "admin/js/calendar.js",
            "admin/contrib/filters/js/DateTimeShortcuts.js",
        ]

    def __init__(self, name: str, *args, **kwargs) -> None:
        self.name = name
        super().__init__(*args, **kwargs)

        self.fields[self.name + "_from"] = forms.SplitDateTimeField(
            label="",
            required=False,
            widget=AdminSplitDateTime(
                attrs={
                    "placeholder": _("Date from"),
                    "class": "vCustomDateField",
                },
            ),
        )
        self.fields[self.name + "_to"] = forms.SplitDateTimeField(
            label="",
            required=False,
            widget=AdminSplitDateTime(
                attrs={
                    "placeholder": _("Date to"),
                    "class": "vCustomDateField",
                },
            ),
        )
```

- [ ] **Step 8: Run all filter tests to verify they pass**

Run: `python -m pytest tests/test_contrib_filters.py -v --no-cov 2>&1 | tail -20`
Expected: All 13 tests pass

- [ ] **Step 9: Commit**

```bash
git add django_admin_boost/admin/contrib/filters/utils.py django_admin_boost/admin/contrib/filters/forms.py tests/test_contrib_filters.py
git commit -m "feat(contrib): add filter utilities and form classes

Port parse_date_str/parse_datetime_str and all filter form classes
from unfold contrib, replacing unfold widgets with Django stock widgets.

refs #16"
```

---

## Task 3: Filters — admin mixins

Port the filter mixin classes that provide shared behavior.

**Files:**
- Create: `django_admin_boost/admin/contrib/filters/admin/__init__.py` (empty initially)
- Create: `django_admin_boost/admin/contrib/filters/admin/mixins.py`
- Modify: `tests/test_contrib_filters.py`

- [ ] **Step 1: Create admin subpackage**

Create empty `django_admin_boost/admin/contrib/filters/admin/__init__.py`.

- [ ] **Step 2: Write tests for mixins**

Append to `tests/test_contrib_filters.py`:

```python
from django.contrib.admin import FieldListFilter, SimpleListFilter

from tests.testapp.models import Article


class ValueMixinTest(TestCase):
    def test_returns_first_item_from_list(self) -> None:
        from django_admin_boost.admin.contrib.filters.admin.mixins import ValueMixin

        obj = ValueMixin()
        obj.lookup_val = ["foo", "bar"]
        assert obj.value() == "foo"

    def test_returns_none_when_no_value(self) -> None:
        from django_admin_boost.admin.contrib.filters.admin.mixins import ValueMixin

        obj = ValueMixin()
        obj.lookup_val = None
        assert obj.value() is None


class MultiValueMixinTest(TestCase):
    def test_returns_list(self) -> None:
        from django_admin_boost.admin.contrib.filters.admin.mixins import MultiValueMixin

        obj = MultiValueMixin()
        obj.lookup_val = ["foo", "bar"]
        assert obj.value() == ["foo", "bar"]


class RangeNumericMixinTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Article.objects.create(title="Cheap", priority=10)
        Article.objects.create(title="Expensive", priority=90)

    def test_filters_queryset_by_range(self) -> None:
        from django_admin_boost.admin.contrib.filters.admin.mixins import RangeNumericMixin

        mixin = RangeNumericMixin.__new__(RangeNumericMixin)
        mixin.parameter_name = "priority"
        mixin.used_parameters = {"priority_from": "10", "priority_to": "50"}
        qs = Article.objects.all()
        result = mixin.queryset(None, qs)
        assert result.count() == 1
        assert result.first().title == "Cheap"

    def test_expected_parameters(self) -> None:
        from django_admin_boost.admin.contrib.filters.admin.mixins import RangeNumericMixin

        mixin = RangeNumericMixin.__new__(RangeNumericMixin)
        mixin.parameter_name = "priority"
        assert mixin.expected_parameters() == ["priority_from", "priority_to"]
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python -m pytest tests/test_contrib_filters.py::ValueMixinTest -v --no-cov 2>&1 | tail -5`
Expected: FAIL — `ImportError`

- [ ] **Step 4: Implement mixins.py**

Create `django_admin_boost/admin/contrib/filters/admin/mixins.py`:

```python
from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any

from django.contrib.admin import (
    ChoicesFieldListFilter,
    ListFilter,
    RelatedFieldListFilter,
)
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.views.main import ChangeList
from django.db.models import QuerySet
from django.db.models.fields import BLANK_CHOICE_DASH
from django.db.models.fields.related import RelatedField
from django.forms import ValidationError
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from django_admin_boost.admin.contrib.filters.forms import (
    AutocompleteDropdownForm,
    CheckboxForm,
    DropdownForm,
    RadioForm,
    RangeNumericForm,
)


class ValueMixin:
    lookup_val = None

    def value(self) -> str | None:
        if isinstance(self.lookup_val, list) and len(self.lookup_val):
            return self.lookup_val[0]

        return self.lookup_val


class MultiValueMixin:
    lookup_val = None

    def value(self) -> list[str] | None:
        return self.lookup_val


class DropdownMixin:
    template = "admin/filters/filters_field.html"
    form_class = DropdownForm
    all_option = ["", _("All")]


class ChoicesMixin(ChoicesFieldListFilter):
    template = "admin/filters/filters_field.html"
    all_option: tuple[str, str] | None = None
    form_class: type[CheckboxForm | RadioForm]
    value: Callable

    def choices(self, changelist: ChangeList) -> Iterator:
        add_facets = getattr(changelist, "add_facets", False)
        facet_counts = self.get_facet_queryset(changelist) if add_facets else None
        choices = [self.all_option] if self.all_option else []

        for i, choice in enumerate(self.field.flatchoices):
            if add_facets and facet_counts:
                count = facet_counts[f"{i}__c"]
                choices.append((choice[0], f"{choice[1]} ({count})"))
            else:
                choices.append(choice)

        yield {
            "form": self.form_class(
                label=_(" By %(filter_title)s ") % {"filter_title": self.title},
                name=self.lookup_kwarg,
                choices=choices,
                data={
                    self.lookup_kwarg: self.value(),
                },
            ),
        }


class RangeNumericMixin(ListFilter):
    request = None
    template = "admin/filters/filters_numeric_range.html"
    parameter_name: str | None = None

    def init_used_parameters(self, params: dict[str, Any]) -> None:
        if f"{self.parameter_name}_from" in params:
            value = params.pop(f"{self.parameter_name}_from")
            self.used_parameters[f"{self.parameter_name}_from"] = (
                value[0] if isinstance(value, list) else value
            )

        if f"{self.parameter_name}_to" in params:
            value = params.pop(f"{self.parameter_name}_to")
            self.used_parameters[f"{self.parameter_name}_to"] = (
                value[0] if isinstance(value, list) else value
            )

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet | None:
        filters = {}

        value_from = self.used_parameters.get(f"{self.parameter_name}_from", None)
        if value_from is not None and value_from != "":
            filters.update(
                {
                    f"{self.parameter_name}__gte": self.used_parameters.get(
                        f"{self.parameter_name}_from",
                        None,
                    ),
                },
            )

        value_to = self.used_parameters.get(f"{self.parameter_name}_to", None)
        if value_to is not None and value_to != "":
            filters.update(
                {
                    f"{self.parameter_name}__lte": self.used_parameters.get(
                        f"{self.parameter_name}_to",
                        None,
                    ),
                },
            )

        try:
            return queryset.filter(**filters)
        except (ValueError, ValidationError):
            return None

    def expected_parameters(self) -> list[str | None]:
        return [
            f"{self.parameter_name}_from",
            f"{self.parameter_name}_to",
        ]

    def choices(self, changelist: ChangeList) -> Iterator:
        if self.parameter_name:
            yield {
                "request": self.request,
                "parameter_name": self.parameter_name,
                "form": RangeNumericForm(
                    name=self.parameter_name,
                    data={
                        f"{self.parameter_name}_from": self.used_parameters.get(
                            f"{self.parameter_name}_from",
                            None,
                        ),
                        f"{self.parameter_name}_to": self.used_parameters.get(
                            f"{self.parameter_name}_to",
                            None,
                        ),
                    },
                ),
            }


class AutocompleteMixin(RelatedFieldListFilter):
    model_admin: ModelAdmin
    form_class: type[AutocompleteDropdownForm]
    value: Callable

    def has_output(self) -> bool:
        return True

    def field_choices(
        self,
        field: RelatedField,
        request: HttpRequest,
        model_admin: ModelAdmin,
    ) -> list[tuple]:
        return [
            ("", BLANK_CHOICE_DASH),
        ]

    def choices(self, changelist: ChangeList) -> Iterator:
        yield {
            "form": self.form_class(
                request=self.request,
                label=_(" By %(filter_title)s ") % {"filter_title": self.title},
                name=self.lookup_kwarg,
                choices=(),
                field=self.field,
                model_admin=self.model_admin,
                data={
                    self.lookup_kwarg: self.value(),
                },
                multiple=self.multiple
                if hasattr(self, "multiple") and isinstance(self.multiple, bool)
                else False,
            ),
        }
```

- [ ] **Step 5: Run mixin tests to verify they pass**

Run: `python -m pytest tests/test_contrib_filters.py -v --no-cov -k "Mixin" 2>&1 | tail -10`
Expected: 4 passed

- [ ] **Step 6: Commit**

```bash
git add django_admin_boost/admin/contrib/filters/admin/
git commit -m "feat(contrib): add filter admin mixins

Port ValueMixin, MultiValueMixin, DropdownMixin, ChoicesMixin,
RangeNumericMixin, and AutocompleteMixin from unfold contrib.

refs #16"
```

---

## Task 4: Filters — text and choice filter classes

Port the text filter and choice-based filter classes.

**Files:**
- Create: `django_admin_boost/admin/contrib/filters/admin/text_filters.py`
- Create: `django_admin_boost/admin/contrib/filters/admin/choice_filters.py`
- Modify: `tests/test_contrib_filters.py`

- [ ] **Step 1: Write tests for text filters**

Append to `tests/test_contrib_filters.py`:

```python
from django.contrib.admin import site as admin_site
from django.contrib.auth.models import User
from django.test import RequestFactory

from tests.testapp.models import Article, Category


class TextFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Article.objects.create(title="Hello World")
        Article.objects.create(title="Goodbye World")

    def test_queryset_filters_by_parameter(self) -> None:
        from django_admin_boost.admin.contrib.filters.admin.text_filters import TextFilter

        class TitleFilter(TextFilter):
            title = "Title"
            parameter_name = "title__icontains"

            def queryset(self, request, queryset):
                if self.value():
                    return queryset.filter(title__icontains=self.value())
                return queryset

        f = TitleFilter(None, {"title__icontains": "Hello"}, Article, None)
        result = f.queryset(None, Article.objects.all())
        assert result.count() == 1


class FieldTextFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Article.objects.create(title="Hello World")
        Article.objects.create(title="Goodbye World")
        cls.superuser = User.objects.create_superuser(
            username="admin", password="password",
        )

    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_filters_by_icontains(self) -> None:
        from django_admin_boost.admin.contrib.filters.admin.text_filters import FieldTextFilter

        from django_admin_boost.admin import ModelAdmin

        class ArticleAdmin(ModelAdmin):
            list_filter = [("title", FieldTextFilter)]

        ma = ArticleAdmin(Article, admin_site)
        request = self.factory.get("/admin/testapp/article/", {"title__icontains": "Hello"})
        request.user = self.superuser
        changelist = ma.get_changelist_instance(request)
        qs = changelist.get_queryset(request)
        assert qs.count() == 1
        assert qs.first().title == "Hello World"
```

- [ ] **Step 2: Run text filter tests to verify they fail**

Run: `python -m pytest tests/test_contrib_filters.py::TextFilterTest -v --no-cov 2>&1 | tail -5`
Expected: FAIL — `ImportError`

- [ ] **Step 3: Implement text_filters.py**

Create `django_admin_boost/admin/contrib/filters/admin/text_filters.py`:

```python
from __future__ import annotations

from collections.abc import Iterator

from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.views.main import ChangeList
from django.db.models import Field, Model
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from django_admin_boost.admin.contrib.filters.admin.mixins import ValueMixin
from django_admin_boost.admin.contrib.filters.forms import SearchForm


class TextFilter(admin.SimpleListFilter):
    template = "admin/filters/filters_field.html"
    form_class = SearchForm

    def has_output(self) -> bool:
        return True

    def lookups(self, request: HttpRequest, model_admin: ModelAdmin) -> tuple:
        return ()

    def choices(self, changelist: ChangeList) -> Iterator:
        yield {
            "form": self.form_class(
                name=self.parameter_name,
                label=_(" By %(filter_title)s ") % {"filter_title": self.title},
                data={self.parameter_name: self.value()},
            ),
        }


class FieldTextFilter(ValueMixin, admin.FieldListFilter):
    template = "admin/filters/filters_field.html"
    form_class = SearchForm

    def __init__(
        self,
        field: Field,
        request: HttpRequest,
        params: dict[str, str],
        model: type[Model],
        model_admin: ModelAdmin,
        field_path: str,
    ) -> None:
        self.lookup_kwarg = f"{field_path}__icontains"
        self.lookup_val = params.get(self.lookup_kwarg)
        super().__init__(field, request, params, model, model_admin, field_path)

    def expected_parameters(self) -> list[str | None]:
        return [self.lookup_kwarg]

    def choices(self, changelist: ChangeList) -> Iterator:
        yield {
            "form": self.form_class(
                label=_(" By %(filter_title)s ") % {"filter_title": self.title},
                name=self.lookup_kwarg,
                data={self.lookup_kwarg: self.value()},
            ),
        }
```

- [ ] **Step 4: Implement choice_filters.py**

Create `django_admin_boost/admin/contrib/filters/admin/choice_filters.py`:

```python
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db.models import Model
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from django_admin_boost.admin.contrib.filters.admin.mixins import (
    ChoicesMixin,
    MultiValueMixin,
    ValueMixin,
)
from django_admin_boost.admin.contrib.filters.forms import (
    CheckboxForm,
    HorizontalRadioForm,
    RadioForm,
)


class RadioFilter(admin.SimpleListFilter):
    template = "admin/filters/filters_field.html"
    form_class = RadioForm
    all_option = ["", _("All")]

    def choices(self, changelist: ChangeList) -> Iterator:
        add_facets = getattr(changelist, "add_facets", False)
        facet_counts = self.get_facet_queryset(changelist) if add_facets else None
        choices = []

        if self.all_option:
            choices = [self.all_option]

        if add_facets:
            for i, (lookup, title) in enumerate(self.lookup_choices):
                choices.append(
                    (lookup, f"{title} ({facet_counts.get(f'{i}__c', '-')})"),
                )
        else:
            choices.extend(self.lookup_choices)

        yield {
            "form": self.form_class(
                label=_(" By %(filter_title)s ") % {"filter_title": self.title},
                name=self.parameter_name,
                choices=choices,
                data={self.parameter_name: self.value()},
            ),
        }


class CheckboxFilter(RadioFilter):
    form_class = CheckboxForm
    all_option = None

    def __init__(
        self,
        request: HttpRequest,
        params: dict[str, Any],
        model: type[Model],
        model_admin: admin.ModelAdmin,
    ) -> None:
        self.request = request
        super().__init__(request, params, model, model_admin)

    def value(self) -> list[str] | None:
        if self.parameter_name:
            return self.request.GET.getlist(self.parameter_name)


class ChoicesRadioFilter(ValueMixin, ChoicesMixin, admin.ChoicesFieldListFilter):
    form_class = RadioForm
    all_option = ["", _("All")]


class ChoicesCheckboxFilter(
    MultiValueMixin,
    ChoicesMixin,
    admin.ChoicesFieldListFilter,
):
    form_class = CheckboxForm
    all_option = None


class BooleanRadioFilter(ValueMixin, admin.BooleanFieldListFilter):
    template = "admin/filters/filters_field.html"
    form_class = HorizontalRadioForm
    all_option = ["", _("All")]

    def choices(self, changelist: ChangeList) -> Iterator:
        add_facets = getattr(changelist, "add_facets", False)
        facet_counts = self.get_facet_queryset(changelist) if add_facets else None

        if add_facets and facet_counts:
            choices = [
                self.all_option,
                *[
                    ("1", f"{_('Yes')} ({facet_counts['true__c']})"),
                    ("0", f"{_('No')} ({facet_counts['false__c']})"),
                ],
            ]
        else:
            choices = [
                self.all_option,
                *[
                    ("1", _("Yes")),
                    ("0", _("No")),
                ],
            ]

        yield {
            "form": self.form_class(
                label=_(" By %(filter_title)s ") % {"filter_title": self.title},
                name=self.lookup_kwarg,
                choices=choices,
                data={self.lookup_kwarg: self.value()},
            ),
        }


class RelatedCheckboxFilter(MultiValueMixin, admin.RelatedFieldListFilter):
    template = "admin/filters/filters_field.html"
    form_class = CheckboxForm

    def choices(self, changelist: ChangeList) -> Iterator:
        add_facets = getattr(changelist, "add_facets", False)
        facet_counts = self.get_facet_queryset(changelist) if add_facets else None

        if add_facets and facet_counts:
            choices = []

            for pk_val, val in self.lookup_choices:
                count = facet_counts[f"{pk_val}__c"]
                choice = (pk_val, f"{val} ({count})")
                choices.append(choice)
        else:
            choices = self.lookup_choices

        yield {
            "form": self.form_class(
                label=_(" By %(filter_title)s ") % {"filter_title": self.title},
                name=self.lookup_kwarg,
                choices=choices,
                data={self.lookup_kwarg: self.value()},
            ),
        }


class AllValuesCheckboxFilter(MultiValueMixin, admin.AllValuesFieldListFilter):
    template = "admin/filters/filters_field.html"
    form_class = CheckboxForm

    def choices(self, changelist: ChangeList) -> Iterator:
        add_facets = getattr(changelist, "add_facets", False)
        facet_counts = self.get_facet_queryset(changelist) if add_facets else None

        if add_facets and facet_counts:
            choices = []

            for i, val in enumerate(self.lookup_choices):
                count = facet_counts[f"{i}__c"]
                choice = (val, f"{val} ({count})")
                choices.append(choice)
        else:
            choices = [[val, val] for _i, val in enumerate(self.lookup_choices)]

        yield {
            "form": self.form_class(
                label=_(" By %(filter_title)s ") % {"filter_title": self.title},
                name=self.lookup_kwarg,
                choices=choices,
                data={self.lookup_kwarg: self.value()},
            ),
        }
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/test_contrib_filters.py -v --no-cov -k "TextFilter or FieldTextFilter" 2>&1 | tail -10`
Expected: pass

- [ ] **Step 6: Commit**

```bash
git add django_admin_boost/admin/contrib/filters/admin/text_filters.py django_admin_boost/admin/contrib/filters/admin/choice_filters.py tests/test_contrib_filters.py
git commit -m "feat(contrib): add text and choice filter classes

refs #16"
```

---

## Task 5: Filters — numeric and datetime filter classes

Port the numeric and datetime filter classes.

**Files:**
- Create: `django_admin_boost/admin/contrib/filters/admin/numeric_filters.py`
- Create: `django_admin_boost/admin/contrib/filters/admin/datetime_filters.py`
- Modify: `tests/test_contrib_filters.py`

- [ ] **Step 1: Write tests for numeric filters**

Append to `tests/test_contrib_filters.py`:

```python
class RangeNumericFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Article.objects.create(title="Low", priority=5)
        Article.objects.create(title="Mid", priority=50)
        Article.objects.create(title="High", priority=95)
        cls.superuser = User.objects.create_superuser(
            username="admin_numeric", password="password",
        )

    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_filters_by_range(self) -> None:
        from django_admin_boost.admin.contrib.filters.admin.numeric_filters import RangeNumericFilter

        from django_admin_boost.admin import ModelAdmin

        class ArticleAdmin(ModelAdmin):
            list_filter = [("priority", RangeNumericFilter)]

        ma = ArticleAdmin(Article, admin_site)
        request = self.factory.get(
            "/admin/testapp/article/", {"priority_from": "10", "priority_to": "60"},
        )
        request.user = self.superuser
        changelist = ma.get_changelist_instance(request)
        qs = changelist.get_queryset(request)
        assert qs.count() == 1
        assert qs.first().title == "Mid"


class SingleNumericFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Article.objects.create(title="Target", priority=42)
        Article.objects.create(title="Other", priority=99)
        cls.superuser = User.objects.create_superuser(
            username="admin_single", password="password",
        )

    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_filters_exact(self) -> None:
        from django_admin_boost.admin.contrib.filters.admin.numeric_filters import SingleNumericFilter

        from django_admin_boost.admin import ModelAdmin

        class ArticleAdmin(ModelAdmin):
            list_filter = [("priority", SingleNumericFilter)]

        ma = ArticleAdmin(Article, admin_site)
        request = self.factory.get("/admin/testapp/article/", {"priority": "42"})
        request.user = self.superuser
        changelist = ma.get_changelist_instance(request)
        qs = changelist.get_queryset(request)
        assert qs.count() == 1
        assert qs.first().title == "Target"
```

- [ ] **Step 2: Write tests for datetime filters**

Append to `tests/test_contrib_filters.py`:

```python
import datetime


class RangeDateFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Article.objects.create(title="Old", publish_date=datetime.date(2025, 1, 1))
        Article.objects.create(title="Recent", publish_date=datetime.date(2026, 3, 15))
        Article.objects.create(title="Future", publish_date=datetime.date(2027, 6, 1))
        cls.superuser = User.objects.create_superuser(
            username="admin_date", password="password",
        )

    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_filters_by_date_range(self) -> None:
        from django_admin_boost.admin.contrib.filters.admin.datetime_filters import RangeDateFilter

        from django_admin_boost.admin import ModelAdmin

        class ArticleAdmin(ModelAdmin):
            list_filter = [("publish_date", RangeDateFilter)]

        ma = ArticleAdmin(Article, admin_site)
        request = self.factory.get(
            "/admin/testapp/article/",
            {"publish_date_from": "2026-01-01", "publish_date_to": "2026-12-31"},
        )
        request.user = self.superuser
        changelist = ma.get_changelist_instance(request)
        qs = changelist.get_queryset(request)
        assert qs.count() == 1
        assert qs.first().title == "Recent"
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python -m pytest tests/test_contrib_filters.py -v --no-cov -k "RangeNumeric or SingleNumeric or RangeDate" 2>&1 | tail -10`
Expected: FAIL — `ImportError`

- [ ] **Step 4: Implement numeric_filters.py**

Create `django_admin_boost/admin/contrib/filters/admin/numeric_filters.py`:

```python
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.views.main import ChangeList
from django.core.validators import EMPTY_VALUES
from django.db.models import Max, Min, Model, QuerySet
from django.db.models.fields import (
    AutoField,
    DecimalField,
    Field,
    FloatField,
    IntegerField,
)
from django.forms import ValidationError
from django.http import HttpRequest

from django_admin_boost.admin.contrib.filters.admin.mixins import RangeNumericMixin
from django_admin_boost.admin.contrib.filters.forms import SingleNumericForm, SliderNumericForm


class SingleNumericFilter(admin.FieldListFilter):
    request = None
    parameter_name = None
    template = "admin/filters/filters_numeric_single.html"

    def __init__(
        self,
        field: Field,
        request: HttpRequest,
        params: dict[str, str],
        model: type[Model],
        model_admin: ModelAdmin,
        field_path: str,
    ) -> None:
        super().__init__(field, request, params, model, model_admin, field_path)

        if not isinstance(field, DecimalField | IntegerField | FloatField | AutoField):
            raise TypeError(
                f"Class {type(self.field)} is not supported for {self.__class__.__name__}.",
            )

        self.request = request

        if self.parameter_name is None:
            self.parameter_name = self.field_path

        if self.parameter_name in params:
            value = params.pop(self.parameter_name)
            value = value[0] if isinstance(value, list) else value

            if value not in EMPTY_VALUES:
                self.used_parameters[self.parameter_name] = value

    def queryset(
        self,
        request: HttpRequest,
        queryset: QuerySet[Any],
    ) -> QuerySet | None:
        if self.value() and self.parameter_name:
            try:
                return queryset.filter(**{self.parameter_name: self.value()})
            except (ValueError, ValidationError):
                return None

    def value(self) -> Any:
        if self.parameter_name:
            return self.used_parameters.get(self.parameter_name)

    def expected_parameters(self) -> list[str | None]:
        return [self.parameter_name]

    def choices(self, changelist: ChangeList) -> Iterator:
        if self.parameter_name:
            yield {
                "request": self.request,
                "parameter_name": self.parameter_name,
                "form": SingleNumericForm(
                    name=self.parameter_name,
                    data={self.parameter_name: self.value()},
                ),
            }


class RangeNumericListFilter(RangeNumericMixin, admin.SimpleListFilter):
    def __init__(
        self,
        request: HttpRequest,
        params: dict[str, str],
        model: type[Model],
        model_admin: ModelAdmin,
    ) -> None:
        super().__init__(request, params, model, model_admin)

        self.request = request
        self.init_used_parameters(params)

    def lookups(
        self,
        request: HttpRequest,
        model_admin: ModelAdmin,
    ) -> tuple[tuple[str, str], ...]:
        return (("dummy", "dummy"),)


class RangeNumericFilter(RangeNumericMixin, admin.FieldListFilter):
    def __init__(
        self,
        field: Field,
        request: HttpRequest,
        params: dict[str, str],
        model: type[Model],
        model_admin: ModelAdmin,
        field_path: str,
    ) -> None:
        super().__init__(field, request, params, model, model_admin, field_path)
        if not isinstance(field, DecimalField | IntegerField | FloatField | AutoField):
            raise TypeError(
                f"Class {type(self.field)} is not supported for {self.__class__.__name__}.",
            )

        self.request = request
        if self.parameter_name is None:
            self.parameter_name = self.field_path

        self.init_used_parameters(params)


class SliderNumericFilter(RangeNumericFilter):
    MAX_DECIMALS = 7
    STEP = None

    template = "admin/filters/filters_numeric_slider.html"
    field = None
    form_class = SliderNumericForm

    def __init__(
        self,
        field: Field,
        request: HttpRequest,
        params: dict[str, str],
        model: type[Model],
        model_admin: ModelAdmin,
        field_path: str,
    ) -> None:
        super().__init__(field, request, params, model, model_admin, field_path)

        self.field = field
        self.q = model_admin.get_queryset(request)

    def choices(self, changelist: ChangeList) -> Iterator:
        total = self.q.all().count()
        min_value = self.q.all().aggregate(min=Min(self.parameter_name)).get("min", 0)
        max_value = None

        if total > 1:
            max_value = (
                self.q.all().aggregate(max=Max(self.parameter_name)).get("max", 0)
            )

        decimals = 0
        step = self.STEP if self.STEP else 1

        if isinstance(self.field, FloatField | DecimalField):
            decimals = self.MAX_DECIMALS
            step = self.STEP if self.STEP else self._get_min_step(self.MAX_DECIMALS)

        if self.parameter_name:
            yield {
                "decimals": decimals,
                "step": step,
                "parameter_name": self.parameter_name,
                "request": self.request,
                "min": min_value,
                "max": max_value,
                "value_from": self.used_parameters.get(
                    self.parameter_name + "_from",
                    min_value,
                ),
                "value_to": self.used_parameters.get(
                    self.parameter_name + "_to",
                    max_value,
                ),
                "form": self.form_class(
                    name=self.parameter_name,
                    min=min_value,
                    max=max_value,
                    data={
                        self.parameter_name
                        + "_from": self.used_parameters.get(
                            self.parameter_name + "_from",
                            min_value,
                        ),
                        self.parameter_name
                        + "_to": self.used_parameters.get(
                            self.parameter_name + "_to",
                            max_value,
                        ),
                    },
                ),
            }

    def _get_min_step(self, precision: int) -> float:
        result_format = f"{{:.{precision - 1}f}}"
        return float(result_format.format(0) + "1")
```

- [ ] **Step 5: Implement datetime_filters.py**

Create `django_admin_boost/admin/contrib/filters/admin/datetime_filters.py`:

```python
from __future__ import annotations

from collections.abc import Iterator

from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.views.main import ChangeList
from django.core.validators import EMPTY_VALUES
from django.db.models import Model, QuerySet
from django.db.models.fields import DateField, DateTimeField, Field
from django.forms import ValidationError
from django.http import HttpRequest

from django_admin_boost.admin.contrib.filters.forms import RangeDateForm, RangeDateTimeForm
from django_admin_boost.admin.contrib.filters.utils import parse_date_str, parse_datetime_str


class RangeDateFilter(admin.FieldListFilter):
    request = None
    parameter_name = None
    form_class = RangeDateForm
    template = "admin/filters/filters_date_range.html"

    def __init__(
        self,
        field: Field,
        request: HttpRequest,
        params: dict[str, str],
        model: type[Model],
        model_admin: ModelAdmin,
        field_path: str,
    ) -> None:
        super().__init__(field, request, params, model, model_admin, field_path)
        if not isinstance(field, DateField):
            raise TypeError(
                f"Class {type(self.field)} is not supported for {self.__class__.__name__}.",
            )

        self.request = request
        if self.parameter_name is None:
            self.parameter_name = self.field_path

        if self.parameter_name + "_from" in params:
            value = params.pop(self.field_path + "_from")
            value = value[0] if isinstance(value, list) else value

            if value not in EMPTY_VALUES:
                self.used_parameters[self.field_path + "_from"] = value

        if self.parameter_name + "_to" in params:
            value = params.pop(self.field_path + "_to")
            value = value[0] if isinstance(value, list) else value

            if value not in EMPTY_VALUES:
                self.used_parameters[self.field_path + "_to"] = value

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet | None:
        filters = {}

        value_from = self.used_parameters.get(f"{self.parameter_name}_from")
        if value_from not in EMPTY_VALUES and isinstance(value_from, str):
            filters.update({f"{self.parameter_name}__gte": parse_date_str(value_from)})

        value_to = self.used_parameters.get(f"{self.parameter_name}_to")
        if value_to not in EMPTY_VALUES and isinstance(value_to, str):
            filters.update({f"{self.parameter_name}__lte": parse_date_str(value_to)})

        try:
            return queryset.filter(**filters)
        except (ValueError, ValidationError):
            return None

    def expected_parameters(self) -> list[str | None]:
        return [
            f"{self.parameter_name}_from",
            f"{self.parameter_name}_to",
        ]

    def choices(self, changelist: ChangeList) -> Iterator:
        yield {
            "request": self.request,
            "parameter_name": self.parameter_name,
            "form": self.form_class(
                name=self.parameter_name,
                data={
                    f"{self.parameter_name}_from": self.used_parameters.get(
                        f"{self.parameter_name}_from",
                        None,
                    ),
                    f"{self.parameter_name}_to": self.used_parameters.get(
                        f"{self.parameter_name}_to",
                        None,
                    ),
                },
            ),
        }


class RangeDateTimeFilter(admin.FieldListFilter):
    request = None
    parameter_name = None
    template = "admin/filters/filters_datetime_range.html"
    form_class = RangeDateTimeForm

    def __init__(
        self,
        field: Field,
        request: HttpRequest,
        params: dict[str, str],
        model: type[Model],
        model_admin: ModelAdmin,
        field_path: str,
    ) -> None:
        super().__init__(field, request, params, model, model_admin, field_path)
        if not isinstance(field, DateTimeField):
            raise TypeError(
                f"Class {type(self.field)} is not supported for {self.__class__.__name__}.",
            )

        self.request = request
        if self.parameter_name is None:
            self.parameter_name = self.field_path

        if self.parameter_name + "_from_0" in params:
            value = params.pop(self.field_path + "_from_0")
            value = value[0] if isinstance(value, list) else value
            self.used_parameters[self.field_path + "_from_0"] = value

        if self.parameter_name + "_from_1" in params:
            value = params.pop(self.field_path + "_from_1")
            value = value[0] if isinstance(value, list) else value
            self.used_parameters[self.field_path + "_from_1"] = value

        if self.parameter_name + "_to_0" in params:
            value = params.pop(self.field_path + "_to_0")
            value = value[0] if isinstance(value, list) else value
            self.used_parameters[self.field_path + "_to_0"] = value

        if self.parameter_name + "_to_1" in params:
            value = params.pop(self.field_path + "_to_1")
            value = value[0] if isinstance(value, list) else value
            self.used_parameters[self.field_path + "_to_1"] = value

    def expected_parameters(self) -> list[str | None]:
        return [
            f"{self.parameter_name}_from_0",
            f"{self.parameter_name}_from_1",
            f"{self.parameter_name}_to_0",
            f"{self.parameter_name}_to_1",
        ]

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet | None:
        filters = {}

        date_value_from = self.used_parameters.get(f"{self.parameter_name}_from_0")
        time_value_from = self.used_parameters.get(f"{self.parameter_name}_from_1")

        date_value_to = self.used_parameters.get(f"{self.parameter_name}_to_0")
        time_value_to = self.used_parameters.get(f"{self.parameter_name}_to_1")

        if date_value_from not in EMPTY_VALUES and time_value_from not in EMPTY_VALUES:
            filters.update(
                {
                    f"{self.parameter_name}__gte": parse_datetime_str(
                        f"{date_value_from} {time_value_from}",
                    ),
                },
            )

        if date_value_to not in EMPTY_VALUES and time_value_to not in EMPTY_VALUES:
            filters.update(
                {
                    f"{self.parameter_name}__lte": parse_datetime_str(
                        f"{date_value_to} {time_value_to}",
                    ),
                },
            )

        try:
            return queryset.filter(**filters)
        except (ValueError, ValidationError):
            return None

    def choices(self, changelist: ChangeList) -> Iterator:
        yield {
            "request": self.request,
            "parameter_name": self.parameter_name,
            "form": self.form_class(
                name=self.parameter_name,
                data={
                    f"{self.parameter_name}_from_0": self.used_parameters.get(
                        f"{self.parameter_name}_from_0",
                    ),
                    f"{self.parameter_name}_from_1": self.used_parameters.get(
                        f"{self.parameter_name}_from_1",
                    ),
                    f"{self.parameter_name}_to_0": self.used_parameters.get(
                        f"{self.parameter_name}_to_0",
                    ),
                    f"{self.parameter_name}_to_1": self.used_parameters.get(
                        f"{self.parameter_name}_to_1",
                    ),
                },
            ),
        }
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `python -m pytest tests/test_contrib_filters.py -v --no-cov -k "RangeNumeric or SingleNumeric or RangeDate" 2>&1 | tail -10`
Expected: pass

- [ ] **Step 7: Commit**

```bash
git add django_admin_boost/admin/contrib/filters/admin/numeric_filters.py django_admin_boost/admin/contrib/filters/admin/datetime_filters.py tests/test_contrib_filters.py
git commit -m "feat(contrib): add numeric and datetime filter classes

refs #16"
```

---

## Task 6: Filters — dropdown, autocomplete, and re-exports

Port dropdown and autocomplete filters, create the `admin/__init__.py` re-exports.

**Files:**
- Create: `django_admin_boost/admin/contrib/filters/admin/dropdown_filters.py`
- Create: `django_admin_boost/admin/contrib/filters/admin/autocomplete_filters.py`
- Modify: `django_admin_boost/admin/contrib/filters/admin/__init__.py`

- [ ] **Step 1: Implement dropdown_filters.py**

Create `django_admin_boost/admin/contrib/filters/admin/dropdown_filters.py`:

```python
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.views.main import ChangeList
from django.core.validators import EMPTY_VALUES
from django.db.models import Field, Model, QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from django_admin_boost.admin.contrib.filters.admin.mixins import (
    DropdownMixin,
    MultiValueMixin,
    ValueMixin,
)
from django_admin_boost.admin.contrib.filters.forms import DropdownForm


class DropdownFilter(admin.SimpleListFilter):
    template = "admin/filters/filters_field.html"
    form_class = DropdownForm
    all_option = ["", _("All")]

    def choices(self, changelist: ChangeList) -> Iterator:
        add_facets = getattr(changelist, "add_facets", False)
        facet_counts = self.get_facet_queryset(changelist) if add_facets else None
        choices = [self.all_option] if self.all_option else []

        for i, choice in enumerate(self.lookup_choices):
            if add_facets and facet_counts:
                count = facet_counts[f"{i}__c"]
                choices.append((choice[0], f"{choice[1]} ({count})"))
            else:
                choices.append(choice)

        yield {
            "form": self.form_class(
                label=_(" By %(filter_title)s ") % {"filter_title": self.title},
                name=self.parameter_name,
                choices=choices,
                data={self.parameter_name: self.value()},
                multiple=self.multiple if hasattr(self, "multiple") else False,
            ),
        }


class MultipleDropdownFilter(DropdownFilter):
    multiple = True
    used_parameters: dict[str, list[str]]

    def __init__(
        self,
        request: HttpRequest,
        params: dict[str, Any],
        model: type[Model],
        model_admin: ModelAdmin,
    ) -> None:
        self.request = request
        super().__init__(request, params, model, model_admin)

        if (
            self.parameter_name is not None
            and isinstance(self.parameter_name, str)
            and self.parameter_name in self.request.GET
        ):
            self.used_parameters[self.parameter_name] = self.request.GET.getlist(
                self.parameter_name,
            )


class ChoicesDropdownFilter(ValueMixin, DropdownMixin, admin.ChoicesFieldListFilter):
    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet | None:
        if self.value() not in EMPTY_VALUES:
            return super().queryset(request, queryset)

        return queryset

    def choices(self, changelist: ChangeList) -> Iterator:
        add_facets = getattr(changelist, "add_facets", False)
        facet_counts = self.get_facet_queryset(changelist) if add_facets else None

        choices = [self.all_option] if self.all_option else []
        for i, choice in enumerate(self.field.flatchoices):
            if add_facets and facet_counts:
                count = facet_counts[f"{i}__c"]
                choices.append((choice[0], f"{choice[1]} ({count})"))
            else:
                choices.append(choice)

        yield {
            "form": self.form_class(
                label=_(" By %(filter_title)s ") % {"filter_title": self.title},
                name=self.lookup_kwarg,
                choices=choices,
                data={self.lookup_kwarg: self.value()},
                multiple=self.multiple if hasattr(self, "multiple") else False,
            ),
        }


class MultipleChoicesDropdownFilter(MultiValueMixin, ChoicesDropdownFilter):
    multiple = True


class RelatedDropdownFilter(ValueMixin, DropdownMixin, admin.RelatedFieldListFilter):
    def __init__(
        self,
        field: Field,
        request: HttpRequest,
        params: dict[str, str],
        model: type[Model],
        model_admin: ModelAdmin,
        field_path: str,
    ) -> None:
        super().__init__(field, request, params, model, model_admin, field_path)
        self.model_admin = model_admin
        self.request = request

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet | None:
        if self.value() not in EMPTY_VALUES:
            return super().queryset(request, queryset)

        return queryset

    def choices(self, changelist: ChangeList) -> Iterator:
        add_facets = getattr(changelist, "add_facets", False)
        facet_counts = self.get_facet_queryset(changelist) if add_facets else None

        if add_facets and facet_counts:
            choices = [self.all_option]

            for pk_val, val in self.lookup_choices:
                count = facet_counts[f"{pk_val}__c"]
                choice = (pk_val, f"{val} ({count})")
                choices.append(choice)
        else:
            choices = [self.all_option, *self.lookup_choices]

        yield {
            "form": self.form_class(
                label=_(" By %(filter_title)s ") % {"filter_title": self.title},
                name=self.lookup_kwarg,
                choices=choices,
                data={self.lookup_kwarg: self.value()},
                multiple=self.multiple if hasattr(self, "multiple") else False,
            ),
        }


class MultipleRelatedDropdownFilter(MultiValueMixin, RelatedDropdownFilter):
    multiple = True
```

- [ ] **Step 2: Implement autocomplete_filters.py**

Create `django_admin_boost/admin/contrib/filters/admin/autocomplete_filters.py`:

```python
from django_admin_boost.admin.contrib.filters.admin.dropdown_filters import (
    MultipleRelatedDropdownFilter,
    RelatedDropdownFilter,
)
from django_admin_boost.admin.contrib.filters.admin.mixins import AutocompleteMixin
from django_admin_boost.admin.contrib.filters.forms import AutocompleteDropdownForm


class AutocompleteSelectFilter(AutocompleteMixin, RelatedDropdownFilter):
    form_class = AutocompleteDropdownForm


class AutocompleteSelectMultipleFilter(
    AutocompleteMixin,
    MultipleRelatedDropdownFilter,
):
    form_class = AutocompleteDropdownForm
```

- [ ] **Step 3: Create admin/__init__.py with all re-exports**

Write `django_admin_boost/admin/contrib/filters/admin/__init__.py`:

```python
from django_admin_boost.admin.contrib.filters.admin.autocomplete_filters import (
    AutocompleteSelectFilter,
    AutocompleteSelectMultipleFilter,
)
from django_admin_boost.admin.contrib.filters.admin.choice_filters import (
    AllValuesCheckboxFilter,
    BooleanRadioFilter,
    CheckboxFilter,
    ChoicesCheckboxFilter,
    ChoicesRadioFilter,
    RadioFilter,
    RelatedCheckboxFilter,
)
from django_admin_boost.admin.contrib.filters.admin.datetime_filters import (
    RangeDateFilter,
    RangeDateTimeFilter,
)
from django_admin_boost.admin.contrib.filters.admin.dropdown_filters import (
    ChoicesDropdownFilter,
    DropdownFilter,
    MultipleChoicesDropdownFilter,
    MultipleDropdownFilter,
    MultipleRelatedDropdownFilter,
    RelatedDropdownFilter,
)
from django_admin_boost.admin.contrib.filters.admin.numeric_filters import (
    RangeNumericFilter,
    RangeNumericListFilter,
    SingleNumericFilter,
    SliderNumericFilter,
)
from django_admin_boost.admin.contrib.filters.admin.text_filters import FieldTextFilter, TextFilter

__all__ = [
    "AllValuesCheckboxFilter",
    "AutocompleteSelectFilter",
    "AutocompleteSelectMultipleFilter",
    "BooleanRadioFilter",
    "CheckboxFilter",
    "ChoicesCheckboxFilter",
    "ChoicesDropdownFilter",
    "ChoicesRadioFilter",
    "DropdownFilter",
    "FieldTextFilter",
    "MultipleChoicesDropdownFilter",
    "MultipleDropdownFilter",
    "MultipleRelatedDropdownFilter",
    "RadioFilter",
    "RangeDateFilter",
    "RangeDateTimeFilter",
    "RangeNumericFilter",
    "RangeNumericListFilter",
    "RelatedCheckboxFilter",
    "RelatedDropdownFilter",
    "SingleNumericFilter",
    "SliderNumericFilter",
    "TextFilter",
]
```

- [ ] **Step 4: Verify all imports work**

Run: `python -c "from django_admin_boost.admin.contrib.filters.admin import *; print('All filter classes imported successfully')" 2>&1` (requires DJANGO_SETTINGS_MODULE set)

Run: `DJANGO_SETTINGS_MODULE=settings.base PYTHONPATH=tests python -c "import django; django.setup(); from django_admin_boost.admin.contrib.filters.admin import TextFilter, RangeDateFilter, SliderNumericFilter, AutocompleteSelectFilter; print('OK')"`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add django_admin_boost/admin/contrib/filters/admin/
git commit -m "feat(contrib): add dropdown, autocomplete filters and re-exports

Completes the full set of 22 filter classes.

refs #16"
```

---

## Task 7: Filters — templates and static assets

Create the Jinja2 and DTL templates, copy static assets from the unfold branch.

**Files:**
- Create: 6 Jinja2 templates in `django_admin_boost/admin/contrib/filters/jinja2/admin/filters/`
- Create: 6 DTL templates in `django_admin_boost/admin/contrib/filters/templates/admin/filters/`
- Create: static assets in `django_admin_boost/admin/contrib/filters/static/admin/contrib/filters/`

- [ ] **Step 1: Create Jinja2 filter templates**

Templates are adapted from the unfold originals with Tailwind classes removed and Django admin-compatible HTML. The templates render filter forms in the admin sidebar.

`django_admin_boost/admin/contrib/filters/jinja2/admin/filters/filters_field.html`:
```html
{% with choices.0 as choice %}
    {% for field in choice.form %}
        <div>{{ field.label_tag() }}{{ field }}</div>
    {% endfor %}
{% endwith %}
```

`django_admin_boost/admin/contrib/filters/jinja2/admin/filters/filters_numeric_range.html`:
```html
{% with choices.0 as choice %}
    <div>
        <h3>{% trans %}By {{ title }}{% endtrans %}</h3>
        {% for field in choice.form %}
            <div>{{ field }}</div>
        {% endfor %}
    </div>
{% endwith %}
```

`django_admin_boost/admin/contrib/filters/jinja2/admin/filters/filters_numeric_single.html`:
```html
{% with choices.0 as choice %}
    <div>
        <h3>{% trans %}By {{ title }}{% endtrans %}</h3>
        {% for field in choice.form %}
            <div>{{ field }}</div>
        {% endfor %}
    </div>
{% endwith %}
```

`django_admin_boost/admin/contrib/filters/jinja2/admin/filters/filters_numeric_slider.html`:
```html
{% with choices.0 as choice %}
    <div class="admin-numeric-filter-wrapper">
        <h3>{% trans %}By {{ title }}{% endtrans %}</h3>

        {% if choice.min is not none and choice.max is not none and choice.step %}
            <div class="admin-numeric-filter-wrapper-group">
                {{ choice.form.as_p() }}
            </div>

            <div class="admin-numeric-filter-slider" data-min="{{ choice.min|unlocalize }}" data-max="{{ choice.max|unlocalize }}" data-decimals="{{ choice.decimals }}" data-step="{{ choice.step|unlocalize }}">
            </div>
        {% else %}
            <div class="admin-numeric-filter-slider-error">
                <p>{{ gettext('Not enough data.') }}</p>
            </div>
        {% endif %}
    </div>
{% endwith %}
```

`django_admin_boost/admin/contrib/filters/jinja2/admin/filters/filters_date_range.html`:
```html
{% with choices.0 as choice %}
    <div>
        <h3>{% trans %}By {{ title }}{% endtrans %}</h3>
        {% for field in choice.form %}
            <div>{{ field }}</div>
        {% endfor %}
    </div>
{% endwith %}
```

`django_admin_boost/admin/contrib/filters/jinja2/admin/filters/filters_datetime_range.html`:
```html
{% with choices.0 as choice %}
    <div>
        <h3>{% trans %}By {{ title }}{% endtrans %}</h3>
        {% for field in choice.form %}
            <div>{{ field }}</div>
        {% endfor %}
    </div>
{% endwith %}
```

- [ ] **Step 2: Create DTL filter templates**

Same templates in DTL syntax under `django_admin_boost/admin/contrib/filters/templates/admin/filters/`.

`filters_field.html`:
```html
{% load i18n %}

{% with choices.0 as choice %}
    {% for field in choice.form %}
        <div>{{ field.label_tag }}{{ field }}</div>
    {% endfor %}
{% endwith %}
```

`filters_numeric_range.html`:
```html
{% load i18n %}

{% with choices.0 as choice %}
    <div>
        <h3>{% blocktranslate with filter_title=title %}By {{ filter_title }}{% endblocktranslate %}</h3>
        {% for field in choice.form %}
            <div>{{ field }}</div>
        {% endfor %}
    </div>
{% endwith %}
```

`filters_numeric_single.html`:
```html
{% load i18n %}

{% with choices.0 as choice %}
    <div>
        <h3>{% blocktranslate with filter_title=title %}By {{ filter_title }}{% endblocktranslate %}</h3>
        {% for field in choice.form %}
            <div>{{ field }}</div>
        {% endfor %}
    </div>
{% endwith %}
```

`filters_numeric_slider.html`:
```html
{% load i18n l10n %}

{% with choices.0 as choice %}
    <div class="admin-numeric-filter-wrapper">
        <h3>{% blocktranslate with filter_title=title %}By {{ filter_title }}{% endblocktranslate %}</h3>

        {% if choice.min != None and choice.max != None and choice.step %}
            <div class="admin-numeric-filter-wrapper-group">
                {{ choice.form.as_p }}
            </div>

            <div class="admin-numeric-filter-slider" data-min="{{ choice.min|unlocalize }}" data-max="{{ choice.max|unlocalize }}" data-decimals="{{ choice.decimals }}" data-step="{{ choice.step|unlocalize }}">
            </div>
        {% else %}
            <div class="admin-numeric-filter-slider-error">
                <p>{% translate 'Not enough data.' %}</p>
            </div>
        {% endif %}
    </div>
{% endwith %}
```

`filters_date_range.html`:
```html
{% load i18n %}

{% with choices.0 as choice %}
    <div>
        <h3>{% blocktranslate with filter_title=title %}By {{ filter_title }}{% endblocktranslate %}</h3>
        {% for field in choice.form %}
            <div>{{ field }}</div>
        {% endfor %}
    </div>
{% endwith %}
```

`filters_datetime_range.html`:
```html
{% load i18n %}

{% with choices.0 as choice %}
    <div>
        <h3>{% blocktranslate with filter_title=title %}By {{ filter_title }}{% endblocktranslate %}</h3>
        {% for field in choice.form %}
            <div>{{ field }}</div>
        {% endfor %}
    </div>
{% endwith %}
```

- [ ] **Step 3: Copy static assets from feat/unfold branch**

Copy the static files from the unfold branch, updating the path prefix from `unfold/filters/` to `admin/contrib/filters/`:

```bash
# From the feat/unfold branch, extract static assets
git show feat/unfold:django_admin_boost/unfold/contrib/filters/static/unfold/filters/css/nouislider/nouislider.min.css > django_admin_boost/admin/contrib/filters/static/admin/contrib/filters/css/nouislider/nouislider.min.css
git show feat/unfold:django_admin_boost/unfold/contrib/filters/static/unfold/filters/css/nouislider/LICENSE > django_admin_boost/admin/contrib/filters/static/admin/contrib/filters/css/nouislider/LICENSE
git show feat/unfold:django_admin_boost/unfold/contrib/filters/static/unfold/filters/js/nouislider/nouislider.min.js > django_admin_boost/admin/contrib/filters/static/admin/contrib/filters/js/nouislider/nouislider.min.js
git show feat/unfold:django_admin_boost/unfold/contrib/filters/static/unfold/filters/js/nouislider/LICENSE > django_admin_boost/admin/contrib/filters/static/admin/contrib/filters/js/nouislider/LICENSE
git show feat/unfold:django_admin_boost/unfold/contrib/filters/static/unfold/filters/js/wnumb/wNumb.min.js > django_admin_boost/admin/contrib/filters/static/admin/contrib/filters/js/wnumb/wNumb.min.js
git show feat/unfold:django_admin_boost/unfold/contrib/filters/static/unfold/filters/js/wnumb/LICENSE > django_admin_boost/admin/contrib/filters/static/admin/contrib/filters/js/wnumb/LICENSE
git show feat/unfold:django_admin_boost/unfold/contrib/filters/static/unfold/filters/js/admin-numeric-filter.js > django_admin_boost/admin/contrib/filters/static/admin/contrib/filters/js/admin-numeric-filter.js
git show feat/unfold:django_admin_boost/unfold/contrib/filters/static/unfold/filters/js/DateTimeShortcuts.js > django_admin_boost/admin/contrib/filters/static/admin/contrib/filters/js/DateTimeShortcuts.js
```

Create the directories first with `mkdir -p`.

- [ ] **Step 4: Create select2.init.js**

Create `django_admin_boost/admin/contrib/filters/static/admin/contrib/filters/js/select2.init.js`:

```javascript
document.addEventListener("DOMContentLoaded", function () {
    // Initialize select2 on filter dropdowns that use the admin-autocomplete class
    if (typeof django !== "undefined" && typeof django.jQuery !== "undefined") {
        django.jQuery(".admin-autocomplete").not("[name*=__prefix__]").select2();
    }
});
```

- [ ] **Step 5: Run existing tests to verify nothing is broken**

Run: `python -m pytest tests/test_contrib_filters.py -v --no-cov 2>&1 | tail -15`
Expected: All tests pass

- [ ] **Step 6: Commit**

```bash
git add django_admin_boost/admin/contrib/filters/jinja2/ django_admin_boost/admin/contrib/filters/templates/ django_admin_boost/admin/contrib/filters/static/
git commit -m "feat(contrib): add filter templates and static assets

Jinja2 + DTL templates for all filter types, bundled nouislider,
wNumb, and DateTimeShortcuts JS. Templates use Django admin CSS
instead of Tailwind.

refs #16"
```

---

## Task 8: Inlines — non-related inline support

Port the non-related inline mixin, formset, and system checks.

**Files:**
- Create: `django_admin_boost/admin/contrib/inlines/checks.py`
- Create: `django_admin_boost/admin/contrib/inlines/forms.py`
- Create: `django_admin_boost/admin/contrib/inlines/admin.py`
- Create: `tests/test_contrib_inlines.py`

- [ ] **Step 1: Write tests for non-related inlines**

Create `tests/test_contrib_inlines.py`:

```python
from django.contrib.admin import site as admin_site
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.test import RequestFactory, TestCase

from django_admin_boost.admin import ModelAdmin
from tests.testapp.models import Article, Category


class NonrelatedInlineMixinTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.category = Category.objects.create(name="News")
        cls.superuser = User.objects.create_superuser(
            username="admin_inline", password="password",
        )

    def test_get_form_queryset_is_required(self) -> None:
        from django_admin_boost.admin.contrib.inlines.admin import NonrelatedStackedInline

        class BadInline(NonrelatedStackedInline):
            model = Category

        inline = BadInline(Article, admin_site)
        request = RequestFactory().get("/admin/")
        request.user = self.superuser
        formset_cls = inline.get_formset(request, obj=self.category)
        with self.assertRaises(NotImplementedError):
            formset_cls.save_new_instance(None, None)

    def test_formset_with_queryset(self) -> None:
        from django_admin_boost.admin.contrib.inlines.admin import NonrelatedStackedInline

        class CategoryInline(NonrelatedStackedInline):
            model = Category

            def get_form_queryset(self, obj) -> QuerySet:
                return Category.objects.filter(pk=obj.pk)

            def save_new_instance(self, parent, instance) -> None:
                instance.save()

        inline = CategoryInline(Article, admin_site)
        request = RequestFactory().get("/admin/")
        request.user = self.superuser
        formset_cls = inline.get_formset(request, obj=self.category)
        assert formset_cls.provided_queryset.count() == 1


class NonrelatedModelAdminChecksTest(TestCase):
    def test_skips_relation_check(self) -> None:
        from django_admin_boost.admin.contrib.inlines.checks import NonrelatedModelAdminChecks

        checks = NonrelatedModelAdminChecks()
        assert checks._check_relation(None, None) == []

    def test_skips_exclude_of_parent_model_check(self) -> None:
        from django_admin_boost.admin.contrib.inlines.checks import NonrelatedModelAdminChecks

        checks = NonrelatedModelAdminChecks()
        assert checks._check_exclude_of_parent_model(None, None) == []


class NonrelatedInlineFormSetTest(TestCase):
    def test_default_prefix(self) -> None:
        from django_admin_boost.admin.contrib.inlines.forms import (
            nonrelated_inline_formset_factory,
        )

        FormSet = nonrelated_inline_formset_factory(
            Category,
            queryset=Category.objects.none(),
            save_new_instance=lambda p, i: None,
        )
        assert FormSet.get_default_prefix() == "testapp-category"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_contrib_inlines.py -v --no-cov 2>&1 | tail -10`
Expected: FAIL — `ImportError`

- [ ] **Step 3: Implement checks.py**

Create `django_admin_boost/admin/contrib/inlines/checks.py`:

```python
from django.contrib.admin.checks import InlineModelAdminChecks
from django.contrib.admin.options import InlineModelAdmin
from django.core.checks import CheckMessage
from django.db.models import Model


class NonrelatedModelAdminChecks(InlineModelAdminChecks):
    def _check_exclude_of_parent_model(
        self,
        obj: InlineModelAdmin,
        parent_model: Model,
    ) -> list[CheckMessage]:
        return []

    def _check_relation(
        self,
        obj: InlineModelAdmin,
        parent_model: Model,
    ) -> list[CheckMessage]:
        return []
```

- [ ] **Step 4: Implement forms.py**

Create `django_admin_boost/admin/contrib/inlines/forms.py`:

```python
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from django.db.models import Model, QuerySet
from django.forms import BaseModelFormSet, ModelForm, modelformset_factory


class NonrelatedInlineModelFormSet(BaseModelFormSet):
    def __init__(
        self,
        instance: Model | None = None,
        save_as_new: bool = False,
        **kwargs: Any,
    ) -> None:
        self.instance = instance
        super().__init__(provided_queryset=self.provided_queryset, **kwargs)

    @classmethod
    def get_default_prefix(cls: BaseModelFormSet) -> str:
        return f"{cls.model._meta.app_label}-{cls.model._meta.model_name}"

    def save_new(self, form: ModelForm, commit: bool = True):
        obj = super().save_new(form, commit=False)
        self.save_new_instance(self.instance, obj)

        if commit:
            obj.save()

        return obj


def nonrelated_inline_formset_factory(
    model: Model,
    queryset: QuerySet | None = None,
    formset: BaseModelFormSet = NonrelatedInlineModelFormSet,
    save_new_instance: Callable | None = None,
    **kwargs: Any,
) -> BaseModelFormSet:
    inline_formset = modelformset_factory(model, formset=formset, **kwargs)
    inline_formset.provided_queryset = queryset
    inline_formset.save_new_instance = save_new_instance
    return inline_formset
```

- [ ] **Step 5: Implement admin.py**

Create `django_admin_boost/admin/contrib/inlines/admin.py`:

```python
from __future__ import annotations

from functools import partial
from typing import Any

from django.contrib.admin.options import InlineModelAdmin
from django.contrib.admin.utils import NestedObjects, flatten_fieldsets
from django.core.exceptions import ValidationError
from django.db import router
from django.db.models import Model, QuerySet
from django.forms.formsets import DELETION_FIELD_NAME
from django.forms.models import ALL_FIELDS, modelform_defines_fields
from django.http import HttpRequest
from django.utils.text import get_text_list
from django.utils.translation import gettext_lazy as _

from django_admin_boost.admin import StackedInline, TabularInline
from django_admin_boost.admin.contrib.inlines.checks import NonrelatedModelAdminChecks
from django_admin_boost.admin.contrib.inlines.forms import (
    NonrelatedInlineModelFormSet,
    nonrelated_inline_formset_factory,
)


class NonrelatedInlineMixin(InlineModelAdmin):
    checks_class = NonrelatedModelAdminChecks
    formset = NonrelatedInlineModelFormSet

    def get_formset(
        self,
        request: HttpRequest,
        obj: Model | None = None,
        **kwargs: Any,
    ):
        defaults = self._get_formset_defaults(request, obj, **kwargs)

        defaults["queryset"] = (
            self.get_form_queryset(obj) if obj else self.model.objects.none()
        )

        return nonrelated_inline_formset_factory(
            self.model,
            save_new_instance=self.save_new_instance,
            **defaults,
        )

    def get_form_queryset(self, obj: Model) -> QuerySet:
        raise NotImplementedError("get_form_queryset must be implemented")

    def save_new_instance(self, parent: Model, instance: Model) -> None:
        raise NotImplementedError("save_new_instance must be implemented")

    def _get_formset_defaults(
        self,
        request: HttpRequest,
        obj: Model | None = None,
        **kwargs: Any,
    ):
        if "fields" in kwargs:
            fields = kwargs.pop("fields")
        else:
            fields = flatten_fieldsets(self.get_fieldsets(request, obj))
        excluded = self.get_exclude(request, obj)
        exclude = [] if excluded is None else list(excluded)
        exclude.extend(self.get_readonly_fields(request, obj))
        if (
            excluded is None
            and hasattr(self.form, "_meta")
            and self.form._meta.exclude
        ):
            exclude.extend(self.form._meta.exclude)
        exclude = exclude or None
        can_delete = self.can_delete and self.has_delete_permission(request, obj)
        defaults = {
            "form": self.form,
            "formset": self.formset,
            "fields": fields,
            "exclude": exclude,
            "formfield_callback": partial(
                self.formfield_for_dbfield,
                request=request,
            ),
            "extra": self.get_extra(request, obj, **kwargs),
            "min_num": self.get_min_num(request, obj, **kwargs),
            "max_num": self.get_max_num(request, obj, **kwargs),
            "can_delete": can_delete,
            **kwargs,
        }

        base_model_form = defaults["form"]
        can_change = self.has_change_permission(request, obj) if request else True
        can_add = self.has_add_permission(request, obj) if request else True

        class DeleteProtectedModelForm(base_model_form):
            def hand_clean_DELETE(self):
                if self.cleaned_data.get(DELETION_FIELD_NAME, False):
                    using = router.db_for_write(self._meta.model)
                    collector = NestedObjects(using=using)
                    if self.instance._state.adding:
                        return
                    collector.collect([self.instance])
                    if collector.protected:
                        objs = []
                        for p in collector.protected:
                            objs.append(
                                _("%(class_name)s %(instance)s")
                                % {
                                    "class_name": p._meta.verbose_name,
                                    "instance": p,
                                },
                            )
                        params = {
                            "class_name": self._meta.model._meta.verbose_name,
                            "instance": self.instance,
                            "related_objects": get_text_list(objs, _("and")),
                        }
                        msg = _(
                            "Deleting %(class_name)s %(instance)s would require "
                            "deleting the following protected related objects: "
                            "%(related_objects)s",
                        )
                        raise ValidationError(
                            msg,
                            code="deleting_protected",
                            params=params,
                        )

            def is_valid(self):
                result = super().is_valid()
                self.hand_clean_DELETE()
                return result

            def has_changed(self):
                if not can_change and not self.instance._state.adding:
                    return False
                if not can_add and self.instance._state.adding:
                    return False
                return super().has_changed()

        defaults["form"] = DeleteProtectedModelForm

        if defaults["fields"] is None and not modelform_defines_fields(
            defaults["form"],
        ):
            defaults["fields"] = ALL_FIELDS

        return defaults


class NonrelatedStackedInline(NonrelatedInlineMixin, StackedInline):
    formset = NonrelatedInlineModelFormSet


class NonrelatedTabularInline(NonrelatedInlineMixin, TabularInline):
    formset = NonrelatedInlineModelFormSet
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `python -m pytest tests/test_contrib_inlines.py -v --no-cov 2>&1 | tail -10`
Expected: All 4 tests pass

- [ ] **Step 7: Commit**

```bash
git add django_admin_boost/admin/contrib/inlines/ tests/test_contrib_inlines.py
git commit -m "feat(contrib): add non-related inline support

Port NonrelatedInlineMixin, formset, and system checks from unfold
contrib. Supports inline forms for models without FK relationships.

refs #16"
```

---

## Task 9: Forms — custom widgets

Port the ArrayWidget and WysiwygWidget.

**Files:**
- Create: `django_admin_boost/admin/contrib/forms/widgets.py`
- Create: `tests/test_contrib_forms.py`

- [ ] **Step 1: Write tests for widgets**

Create `tests/test_contrib_forms.py`:

```python
from django.test import TestCase


class ArrayWidgetTest(TestCase):
    def test_decompress_list(self) -> None:
        from django_admin_boost.admin.contrib.forms.widgets import ArrayWidget

        widget = ArrayWidget()
        assert widget.decompress(["a", "b"]) == ["a", "b"]

    def test_decompress_csv_string(self) -> None:
        from django_admin_boost.admin.contrib.forms.widgets import ArrayWidget

        widget = ArrayWidget()
        assert widget.decompress("a,b,c") == ["a", "b", "c"]

    def test_decompress_none(self) -> None:
        from django_admin_boost.admin.contrib.forms.widgets import ArrayWidget

        widget = ArrayWidget()
        assert widget.decompress(None) == []

    def test_value_from_datadict_filters_empty(self) -> None:
        from django.http import QueryDict

        from django_admin_boost.admin.contrib.forms.widgets import ArrayWidget

        widget = ArrayWidget()
        data = QueryDict(mutable=True)
        data.setlist("tags", ["foo", "", "bar"])
        result = widget.value_from_datadict(data, {}, "tags")
        assert result == ["foo", "bar"]

    def test_custom_widget_class(self) -> None:
        from django.forms import NumberInput

        from django_admin_boost.admin.contrib.forms.widgets import ArrayWidget

        widget = ArrayWidget(widget_class=NumberInput)
        instance = widget.get_widget_instance()
        assert isinstance(instance, NumberInput)


class WysiwygWidgetTest(TestCase):
    def test_template_name(self) -> None:
        from django_admin_boost.admin.contrib.forms.widgets import WysiwygWidget

        widget = WysiwygWidget()
        assert widget.template_name == "admin/forms/wysiwyg.html"

    def test_media_includes_trix(self) -> None:
        from django_admin_boost.admin.contrib.forms.widgets import WysiwygWidget

        widget = WysiwygWidget()
        js = widget.media._js
        assert any("trix.js" in path for path in js)

        css = widget.media._css.get("all", ())
        assert any("trix.css" in path for path in css)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_contrib_forms.py -v --no-cov 2>&1 | tail -10`
Expected: FAIL — `ImportError`

- [ ] **Step 3: Implement widgets.py**

Create `django_admin_boost/admin/contrib/forms/widgets.py`:

```python
from __future__ import annotations

from typing import Any

from django.contrib.admin.widgets import AdminTextInputWidget
from django.core.validators import EMPTY_VALUES
from django.forms import MultiWidget, Select, Widget
from django.http import QueryDict
from django.utils.datastructures import MultiValueDict


class ArrayWidget(MultiWidget):
    template_name = "admin/forms/array.html"

    def __init__(
        self,
        widget_class: type[Widget] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.choices = kwargs.get("choices")
        self.widget_class = widget_class

        widgets = [self.get_widget_instance()]
        super().__init__(widgets, attrs=kwargs.get("attrs", None))

    def get_widget_instance(self) -> Any:
        if hasattr(self, "widget_class") and self.widget_class is not None:
            return self.widget_class()

        if hasattr(self, "choices") and self.choices is not None:
            return Select(choices=self.choices)

        return AdminTextInputWidget()

    def get_context(self, name: str, value: Any, attrs: dict | None) -> dict:
        self._resolve_widgets(value)
        context = super().get_context(name, value, attrs)
        context.update(
            {
                "template": self.get_widget_instance().get_context(name, "", {})[
                    "widget"
                ],
            },
        )
        return context

    def value_from_datadict(
        self,
        data: QueryDict,
        files: MultiValueDict,
        name: str,
    ) -> list:
        values = []

        for item in data.getlist(name):
            if item not in EMPTY_VALUES:
                values.append(item)

        return values

    def value_omitted_from_data(
        self,
        data: QueryDict,
        files: MultiValueDict,
        name: str,
    ) -> bool:
        return data.getlist(name) not in [[""], *EMPTY_VALUES]

    def decompress(self, value: Any) -> list:
        if isinstance(value, list):
            return value
        elif isinstance(value, str):
            return value.split(",")

        return []

    def _resolve_widgets(self, value: list | str | None) -> None:
        if value is None:
            value = []
        elif isinstance(value, list):
            self.widgets = [self.get_widget_instance() for item in value]
        else:
            self.widgets = [self.get_widget_instance() for item in value.split(",")]

        self.widgets_names = ["" for i in range(len(self.widgets))]
        self.widgets = [w if isinstance(w, type) else w for w in self.widgets]


class WysiwygWidget(Widget):
    template_name = "admin/forms/wysiwyg.html"

    class Media:
        css = {"all": ("admin/contrib/forms/css/trix/trix.css",)}
        js = (
            "admin/contrib/forms/js/trix/trix.js",
            "admin/contrib/forms/js/trix.config.js",
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_contrib_forms.py -v --no-cov 2>&1 | tail -10`
Expected: All 7 tests pass

- [ ] **Step 5: Commit**

```bash
git add django_admin_boost/admin/contrib/forms/widgets.py tests/test_contrib_forms.py
git commit -m "feat(contrib): add ArrayWidget and WysiwygWidget

Port custom form widgets from unfold contrib, replacing unfold
widgets with Django stock admin widgets.

refs #16"
```

---

## Task 10: Forms — templates and static assets

Create the form widget templates and copy Trix/Alpine static assets.

**Files:**
- Create: Jinja2 templates in `django_admin_boost/admin/contrib/forms/jinja2/admin/forms/`
- Create: DTL templates in `django_admin_boost/admin/contrib/forms/templates/admin/forms/`
- Create: static assets in `django_admin_boost/admin/contrib/forms/static/admin/contrib/forms/`

- [ ] **Step 1: Create Jinja2 form templates**

`django_admin_boost/admin/contrib/forms/jinja2/admin/forms/array.html`:
```html
<div data-controller="array-widget">
    {% for subwidget in widget.subwidgets %}
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            {% with widget=subwidget %}
                {% include widget.template_name %}
            {% endwith %}
            <a onclick="this.parentElement.remove()" style="cursor: pointer; margin-left: 8px; color: #ba2121;" title="{{ gettext('Remove') }}">&times;</a>
        </div>
    {% endfor %}

    <template id="array-widget-template-{{ widget.name }}">
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            {% with widget=template %}
                {% include template.template_name %}
            {% endwith %}
            <a onclick="this.parentElement.remove()" style="cursor: pointer; margin-left: 8px; color: #ba2121;" title="{{ gettext('Remove') }}">&times;</a>
        </div>
    </template>

    <div style="margin-top: 4px;">
        <a onclick="
            var tpl = document.getElementById('array-widget-template-{{ widget.name }}');
            var clone = tpl.content.cloneNode(true);
            var input = clone.querySelector('input, select');
            if (input && input.name.includes('__prefix__')) { input.name = '{{ widget.name }}'; }
            tpl.parentElement.insertBefore(clone, tpl);
        " class="addlink" style="cursor: pointer;">{{ gettext("Add new item") }}</a>
    </div>
</div>
```

`django_admin_boost/admin/contrib/forms/jinja2/admin/forms/wysiwyg.html`:
```html
{% include "admin/forms/helpers/toolbar.html" %}

<input type="hidden" name="{{ widget.name }}" id="wysiwyg-{{ widget.name }}"{% if widget.value != None %} value="{{ widget.value }}"{% endif %} {% include "django/forms/widgets/attrs.html" %}>

<div>
    <trix-editor input="wysiwyg-{{ widget.name }}" {% include "django/forms/widgets/attrs.html" %}></trix-editor>
</div>
```

`django_admin_boost/admin/contrib/forms/jinja2/admin/forms/helpers/toolbar.html`:
```html
<template id="trix-toolbar">
    <div style="display: flex; flex-wrap: wrap; gap: 8px; padding: 8px; border: 1px solid #ddd; border-bottom: none; background: #f8f8f8;">
        <div style="display: flex;">
            <button type="button" data-trix-attribute="bold" data-trix-key="b" title="{{ gettext('Bold') }}" tabindex="-1" style="cursor: pointer; padding: 4px 8px;">B</button>
            <button type="button" data-trix-attribute="italic" data-trix-key="i" title="{{ gettext('Italic') }}" tabindex="-1" style="cursor: pointer; padding: 4px 8px;"><em>I</em></button>
            <button type="button" data-trix-attribute="underlined" data-trix-key="u" title="{{ gettext('Underlined') }}" tabindex="-1" style="cursor: pointer; padding: 4px 8px;"><u>U</u></button>
            <button type="button" data-trix-attribute="strike" title="{{ gettext('Strike') }}" tabindex="-1" style="cursor: pointer; padding: 4px 8px;"><s>S</s></button>
            <button type="button" data-trix-attribute="href" data-trix-action="link" data-trix-key="k" title="{{ gettext('Link') }}" tabindex="-1" style="cursor: pointer; padding: 4px 8px;">&#128279;</button>
        </div>

        <div style="display: flex;">
            <button type="button" data-trix-attribute="heading1" title="{{ gettext('Heading') }} 1" tabindex="-1" style="cursor: pointer; padding: 4px 8px;">H1</button>
            <button type="button" data-trix-attribute="heading2" title="{{ gettext('Heading') }} 2" tabindex="-1" style="cursor: pointer; padding: 4px 8px;">H2</button>
            <button type="button" data-trix-attribute="heading3" title="{{ gettext('Heading') }} 3" tabindex="-1" style="cursor: pointer; padding: 4px 8px;">H3</button>
        </div>

        <div style="display: flex;">
            <button type="button" data-trix-attribute="quote" title="{{ gettext('Quote') }}" tabindex="-1" style="cursor: pointer; padding: 4px 8px;">&ldquo;</button>
            <button type="button" data-trix-attribute="code" title="{{ gettext('Code') }}" tabindex="-1" style="cursor: pointer; padding: 4px 8px;">&lt;/&gt;</button>
            <button type="button" data-trix-attribute="bullet" title="{{ gettext('Unordered list') }}" tabindex="-1" style="cursor: pointer; padding: 4px 8px;">&#8226;</button>
            <button type="button" data-trix-attribute="number" title="{{ gettext('Ordered list') }}" tabindex="-1" style="cursor: pointer; padding: 4px 8px;">1.</button>
        </div>

        <div style="display: flex; margin-left: auto;">
            <button type="button" data-trix-action="undo" data-trix-key="z" title="{{ gettext('Undo') }}" tabindex="-1" style="cursor: pointer; padding: 4px 8px;">&#8617;</button>
            <button type="button" data-trix-action="redo" data-trix-key="shift+z" title="{{ gettext('Redo') }}" tabindex="-1" style="cursor: pointer; padding: 4px 8px;">&#8618;</button>
        </div>

        <div data-trix-dialogs>
            <div data-trix-dialog="href" data-trix-dialog-attribute="href" style="display: none; padding: 8px; background: #f8f8f8; border: 1px solid #ddd;">
                <input type="url" name="href" placeholder="{{ gettext('Enter a URL') }}" required data-trix-input style="padding: 4px 8px;">
                <button type="button" data-trix-method="setAttribute" style="cursor: pointer; padding: 4px 8px;">{{ gettext("Link") }}</button>
                <button type="button" data-trix-method="removeAttribute" style="cursor: pointer; padding: 4px 8px;">{{ gettext("Unlink") }}</button>
            </div>
        </div>
    </div>
</template>
```

- [ ] **Step 2: Create DTL form templates**

Mirror the same templates with DTL syntax under `django_admin_boost/admin/contrib/forms/templates/admin/forms/`.

`array.html`:
```html
{% load i18n %}

<div data-controller="array-widget">
    {% for subwidget in widget.subwidgets %}
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            {% with widget=subwidget %}
                {% include widget.template_name %}
            {% endwith %}
            <a onclick="this.parentElement.remove()" style="cursor: pointer; margin-left: 8px; color: #ba2121;" title="{% translate 'Remove' %}">&times;</a>
        </div>
    {% endfor %}

    <template id="array-widget-template-{{ widget.name }}">
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            {% with widget=template %}
                {% include template.template_name %}
            {% endwith %}
            <a onclick="this.parentElement.remove()" style="cursor: pointer; margin-left: 8px; color: #ba2121;" title="{% translate 'Remove' %}">&times;</a>
        </div>
    </template>

    <div style="margin-top: 4px;">
        <a onclick="
            var tpl = document.getElementById('array-widget-template-{{ widget.name }}');
            var clone = tpl.content.cloneNode(true);
            var input = clone.querySelector('input, select');
            if (input && input.name.includes('__prefix__')) { input.name = '{{ widget.name }}'; }
            tpl.parentElement.insertBefore(clone, tpl);
        " class="addlink" style="cursor: pointer;">{% translate "Add new item" %}</a>
    </div>
</div>
```

`wysiwyg.html`:
```html
{% include "admin/forms/helpers/toolbar.html" %}

<input type="hidden" name="{{ widget.name }}" id="wysiwyg-{{ widget.name }}"{% if widget.value != None %} value="{{ widget.value }}"{% endif %} {% include "django/forms/widgets/attrs.html" %}>

<div>
    <trix-editor input="wysiwyg-{{ widget.name }}" {% include "django/forms/widgets/attrs.html" %}></trix-editor>
</div>
```

`helpers/toolbar.html`:
```html
{% load i18n %}

<template id="trix-toolbar">
    <div style="display: flex; flex-wrap: wrap; gap: 8px; padding: 8px; border: 1px solid #ddd; border-bottom: none; background: #f8f8f8;">
        <div style="display: flex;">
            <button type="button" data-trix-attribute="bold" data-trix-key="b" title="{% translate 'Bold' %}" tabindex="-1" style="cursor: pointer; padding: 4px 8px;">B</button>
            <button type="button" data-trix-attribute="italic" data-trix-key="i" title="{% translate 'Italic' %}" tabindex="-1" style="cursor: pointer; padding: 4px 8px;"><em>I</em></button>
            <button type="button" data-trix-attribute="underlined" data-trix-key="u" title="{% translate 'Underlined' %}" tabindex="-1" style="cursor: pointer; padding: 4px 8px;"><u>U</u></button>
            <button type="button" data-trix-attribute="strike" title="{% translate 'Strike' %}" tabindex="-1" style="cursor: pointer; padding: 4px 8px;"><s>S</s></button>
            <button type="button" data-trix-attribute="href" data-trix-action="link" data-trix-key="k" title="{% translate 'Link' %}" tabindex="-1" style="cursor: pointer; padding: 4px 8px;">&#128279;</button>
        </div>

        <div style="display: flex;">
            <button type="button" data-trix-attribute="heading1" title="{% translate 'Heading' %} 1" tabindex="-1" style="cursor: pointer; padding: 4px 8px;">H1</button>
            <button type="button" data-trix-attribute="heading2" title="{% translate 'Heading' %} 2" tabindex="-1" style="cursor: pointer; padding: 4px 8px;">H2</button>
            <button type="button" data-trix-attribute="heading3" title="{% translate 'Heading' %} 3" tabindex="-1" style="cursor: pointer; padding: 4px 8px;">H3</button>
        </div>

        <div style="display: flex;">
            <button type="button" data-trix-attribute="quote" title="{% translate 'Quote' %}" tabindex="-1" style="cursor: pointer; padding: 4px 8px;">&ldquo;</button>
            <button type="button" data-trix-attribute="code" title="{% translate 'Code' %}" tabindex="-1" style="cursor: pointer; padding: 4px 8px;">&lt;/&gt;</button>
            <button type="button" data-trix-attribute="bullet" title="{% translate 'Unordered list' %}" tabindex="-1" style="cursor: pointer; padding: 4px 8px;">&#8226;</button>
            <button type="button" data-trix-attribute="number" title="{% translate 'Ordered list' %}" tabindex="-1" style="cursor: pointer; padding: 4px 8px;">1.</button>
        </div>

        <div style="display: flex; margin-left: auto;">
            <button type="button" data-trix-action="undo" data-trix-key="z" title="{% translate 'Undo' %}" tabindex="-1" style="cursor: pointer; padding: 4px 8px;">&#8617;</button>
            <button type="button" data-trix-action="redo" data-trix-key="shift+z" title="{% translate 'Redo' %}" tabindex="-1" style="cursor: pointer; padding: 4px 8px;">&#8618;</button>
        </div>

        <div data-trix-dialogs>
            <div data-trix-dialog="href" data-trix-dialog-attribute="href" style="display: none; padding: 8px; background: #f8f8f8; border: 1px solid #ddd;">
                <input type="url" name="href" placeholder="{% translate 'Enter a URL' %}" required data-trix-input style="padding: 4px 8px;">
                <button type="button" data-trix-method="setAttribute" style="cursor: pointer; padding: 4px 8px;">{% translate "Link" %}</button>
                <button type="button" data-trix-method="removeAttribute" style="cursor: pointer; padding: 4px 8px;">{% translate "Unlink" %}</button>
            </div>
        </div>
    </div>
</template>
```

- [ ] **Step 3: Copy static assets from feat/unfold branch**

```bash
# Copy Trix assets
git show feat/unfold:django_admin_boost/unfold/contrib/forms/static/unfold/forms/css/trix/trix.css > django_admin_boost/admin/contrib/forms/static/admin/contrib/forms/css/trix/trix.css
git show feat/unfold:django_admin_boost/unfold/contrib/forms/static/unfold/forms/css/trix/LICENSE > django_admin_boost/admin/contrib/forms/static/admin/contrib/forms/css/trix/LICENSE
git show feat/unfold:django_admin_boost/unfold/contrib/forms/static/unfold/forms/js/trix/trix.js > django_admin_boost/admin/contrib/forms/static/admin/contrib/forms/js/trix/trix.js
git show feat/unfold:django_admin_boost/unfold/contrib/forms/static/unfold/forms/js/trix/LICENSE > django_admin_boost/admin/contrib/forms/static/admin/contrib/forms/js/trix/LICENSE
git show feat/unfold:django_admin_boost/unfold/contrib/forms/static/unfold/forms/js/trix.config.js > django_admin_boost/admin/contrib/forms/static/admin/contrib/forms/js/trix.config.js
```

Create the directories first with `mkdir -p`.

Note: Alpine.js is no longer needed — the array widget template was rewritten to use vanilla JS with `<template>` element cloning instead of Alpine.js directives.

- [ ] **Step 4: Run all tests to verify nothing is broken**

Run: `python -m pytest tests/ -v --no-cov 2>&1 | tail -20`
Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add django_admin_boost/admin/contrib/forms/jinja2/ django_admin_boost/admin/contrib/forms/templates/ django_admin_boost/admin/contrib/forms/static/
git commit -m "feat(contrib): add form widget templates and static assets

Trix editor toolbar uses text labels instead of Material Symbols icons.
Array widget uses vanilla JS <template> cloning instead of Alpine.js.

refs #16"
```

---

## Task 11: Final verification and cleanup

Run the full test suite and verify everything works together.

**Files:**
- No new files

- [ ] **Step 1: Run full test suite**

Run: `python -m pytest tests/ -v --no-cov 2>&1`
Expected: All tests pass, no import errors

- [ ] **Step 2: Verify import ergonomics**

Run:
```bash
DJANGO_SETTINGS_MODULE=settings.base PYTHONPATH=tests python -c "
import django; django.setup()

# Filters
from django_admin_boost.admin.contrib.filters.admin import (
    TextFilter, FieldTextFilter,
    RadioFilter, CheckboxFilter, BooleanRadioFilter,
    RangeDateFilter, RangeDateTimeFilter,
    SingleNumericFilter, RangeNumericFilter, SliderNumericFilter,
    DropdownFilter, RelatedDropdownFilter,
    AutocompleteSelectFilter,
)

# Inlines
from django_admin_boost.admin.contrib.inlines.admin import (
    NonrelatedInlineMixin, NonrelatedStackedInline, NonrelatedTabularInline,
)

# Forms
from django_admin_boost.admin.contrib.forms.widgets import ArrayWidget, WysiwygWidget

print('All contrib imports OK')
"
```
Expected: `All contrib imports OK`

- [ ] **Step 3: Run ruff**

Run: `ruff check django_admin_boost/admin/contrib/ && ruff format --check django_admin_boost/admin/contrib/`
Expected: No errors

- [ ] **Step 4: Run mypy**

Run: `mypy django_admin_boost/admin/contrib/`
Expected: No blocking errors (some type-ignore may be needed for Django internals)

- [ ] **Step 5: Fix any lint/type issues found in steps 3-4**

Address any ruff or mypy issues. Commit fixes.

- [ ] **Step 6: Final commit**

```bash
git commit -m "chore(contrib): fix lint and type issues

refs #16"
```
