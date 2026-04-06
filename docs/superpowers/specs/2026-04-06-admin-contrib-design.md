# Admin Contrib Modules — Design Spec

**Issue:** [#16 — Port useful unfold contrib features to the standard admin](https://github.com/oliverhaas/django-admin-boost/issues/16)
**Date:** 2026-04-06
**Approach:** Direct port from `django_admin_boost.unfold.contrib`, replacing unfold-specific widgets/utilities with standard Django admin equivalents.

## Motivation

The unfold contrib modules provide features that Django's stock admin lacks: advanced filters (numeric range, date range, autocomplete, dropdown, text, checkbox/radio), non-related inlines, and custom widgets (array input, WYSIWYG editor). These features are useful independent of unfold's visual theme and should be available to users of the standard admin replacement (`django_admin_boost.admin`).

## Package Structure

Three new Django apps under `django_admin_boost/admin/contrib/`:

```
django_admin_boost/admin/contrib/
├── __init__.py                          (empty)
│
├── filters/                             App: django_admin_boost.admin.contrib.filters
│   ├── __init__.py
│   ├── apps.py                          AppConfig (label="boost_filters")
│   ├── forms.py                         Filter form classes
│   ├── utils.py                         parse_date_str, parse_datetime_str
│   ├── admin/
│   │   ├── __init__.py                  Re-exports all filter classes
│   │   ├── mixins.py                    ValueMixin, MultiValueMixin, DropdownMixin,
│   │   │                                ChoicesMixin, RangeNumericMixin, AutocompleteMixin
│   │   ├── text_filters.py              TextFilter, FieldTextFilter
│   │   ├── choice_filters.py            RadioFilter, CheckboxFilter, ChoicesRadioFilter,
│   │   │                                ChoicesCheckboxFilter, BooleanRadioFilter,
│   │   │                                RelatedCheckboxFilter, AllValuesCheckboxFilter
│   │   ├── datetime_filters.py          RangeDateFilter, RangeDateTimeFilter
│   │   ├── numeric_filters.py           SingleNumericFilter, RangeNumericFilter,
│   │   │                                RangeNumericListFilter, SliderNumericFilter
│   │   ├── dropdown_filters.py          DropdownFilter, MultipleDropdownFilter,
│   │   │                                ChoicesDropdownFilter, MultipleChoicesDropdownFilter,
│   │   │                                RelatedDropdownFilter, MultipleRelatedDropdownFilter
│   │   └── autocomplete_filters.py      AutocompleteSelectFilter,
│   │                                    AutocompleteSelectMultipleFilter
│   ├── jinja2/admin/filters/            Jinja2 templates (6 files)
│   │   ├── filters_field.html
│   │   ├── filters_numeric_range.html
│   │   ├── filters_numeric_single.html
│   │   ├── filters_numeric_slider.html
│   │   ├── filters_date_range.html
│   │   └── filters_datetime_range.html
│   ├── templates/admin/filters/         DTL mirror templates (6 files)
│   └── static/admin/contrib/filters/    Static assets
│       ├── css/nouislider/nouislider.min.css
│       ├── js/nouislider/nouislider.min.js
│       ├── js/wnumb/wNumb.min.js
│       ├── js/admin-numeric-filter.js
│       ├── js/DateTimeShortcuts.js
│       └── js/select2.init.js
│
├── inlines/                             App: django_admin_boost.admin.contrib.inlines
│   ├── __init__.py
│   ├── apps.py                          AppConfig (label="boost_inlines")
│   ├── admin.py                         NonrelatedInlineMixin, NonrelatedStackedInline,
│   │                                    NonrelatedTabularInline
│   ├── forms.py                         NonrelatedInlineModelFormSet,
│   │                                    nonrelated_inline_formset_factory
│   └── checks.py                        NonrelatedModelAdminChecks
│
└── forms/                               App: django_admin_boost.admin.contrib.forms
    ├── __init__.py
    ├── apps.py                          AppConfig (label="boost_forms")
    ├── widgets.py                       ArrayWidget, WysiwygWidget
    ├── jinja2/admin/forms/              Jinja2 templates
    │   ├── array.html
    │   ├── wysiwyg.html
    │   └── helpers/toolbar.html
    ├── templates/admin/forms/           DTL mirror templates
    └── static/admin/contrib/forms/      Static assets
        ├── css/trix/trix.css
        ├── js/trix/trix.js
        └── js/trix.config.js
```

## Adaptation from Unfold

### Widget replacements

The unfold code uses custom Tailwind-styled widgets. We replace these with Django's stock admin widgets:

| Unfold widget | Standard admin replacement |
|---|---|
| `UnfoldAdminTextInputWidget` | `django.contrib.admin.widgets.AdminTextInputWidget` |
| `UnfoldAdminSelectWidget` | `django.forms.Select` |
| `UnfoldAdminSelectMultipleWidget` | `django.forms.SelectMultiple` |
| `UnfoldAdminRadioSelectWidget` | `django.contrib.admin.widgets.AdminRadioSelect` |
| `UnfoldAdminCheckboxSelectMultipleWidget` | `django.forms.CheckboxSelectMultiple` |
| `UnfoldAdminSplitDateTimeVerticalWidget` | `django.contrib.admin.widgets.AdminSplitDateTime` |
| `INPUT_CLASSES` (Tailwind CSS) | Dropped — use Django admin default CSS |
| `PROSE_CLASSES` / `WYSIWYG_CLASSES` | Dropped — use Django admin default CSS |

### Import replacements

| Unfold import | Standard admin replacement |
|---|---|
| `django_admin_boost.unfold.admin.StackedInline` | `django_admin_boost.admin.StackedInline` |
| `django_admin_boost.unfold.admin.TabularInline` | `django_admin_boost.admin.TabularInline` |
| `django_admin_boost.unfold.utils.parse_date_str` | `django_admin_boost.admin.contrib.filters.utils.parse_date_str` |
| `django_admin_boost.unfold.utils.parse_datetime_str` | `django_admin_boost.admin.contrib.filters.utils.parse_datetime_str` |
| `django_admin_boost.unfold.forms.PaginationFormSetMixin` | Dropped (unfold-specific) |

### Template path changes

All templates move from `unfold/` prefix to `admin/` prefix:

| Unfold template | Standard admin template |
|---|---|
| `unfold/filters/filters_field.html` | `admin/filters/filters_field.html` |
| `unfold/filters/filters_numeric_range.html` | `admin/filters/filters_numeric_range.html` |
| `unfold/filters/filters_numeric_single.html` | `admin/filters/filters_numeric_single.html` |
| `unfold/filters/filters_numeric_slider.html` | `admin/filters/filters_numeric_slider.html` |
| `unfold/filters/filters_date_range.html` | `admin/filters/filters_date_range.html` |
| `unfold/filters/filters_datetime_range.html` | `admin/filters/filters_datetime_range.html` |
| `unfold/forms/array.html` | `admin/forms/array.html` |
| `unfold/forms/wysiwyg.html` | `admin/forms/wysiwyg.html` |

### Static asset path changes

| Unfold static path | Standard admin static path |
|---|---|
| `unfold/filters/css/...` | `admin/contrib/filters/css/...` |
| `unfold/filters/js/...` | `admin/contrib/filters/js/...` |
| `unfold/forms/css/...` | `admin/contrib/forms/css/...` |
| `unfold/forms/js/...` | `admin/contrib/forms/js/...` |

### Utilities (self-contained copy)

`filters/utils.py` contains two functions copied from `unfold.utils`:

```python
def parse_date_str(value: str) -> datetime.date | None:
    """Parse a date string using Django's DATE_INPUT_FORMATS."""

def parse_datetime_str(value: str) -> datetime.datetime | None:
    """Parse a datetime string using Django's DATETIME_INPUT_FORMATS."""
```

### Template restyling

All unfold templates use Tailwind CSS classes extensively. These must be restyled for Django admin's default CSS. The restyling is straightforward for most templates (replacing Tailwind classes with Django admin equivalents or removing them), but two cases require special attention:

**ArrayWidget template** uses Alpine.js (`x-data`, `x-for`, `x-on:click`, `x-init`) in unfold for dynamic add/remove of items. We rewrite this with vanilla JS using `<template>` element cloning to avoid the Alpine.js dependency entirely.

**WysiwygWidget toolbar template** uses Material Symbols (Google icon font) for toolbar buttons. We replace these with text labels or Django admin's existing icon approach to avoid the external font dependency.

### Select2 for dropdown/autocomplete filters

The unfold dropdown and autocomplete filter forms reference `unfold/js/select2.init.js`. Django's admin already ships select2 and jQuery. We provide a minimal `select2.init.js` in our static assets that initializes select2 on filter dropdowns, reusing Django's bundled select2/jQuery.

### Inlines: PaginationFormSetMixin dropped

The unfold `NonrelatedInlineModelFormSet` inherits from `PaginationFormSetMixin` which adds unfold-specific pagination to formsets. The standard admin version inherits from `BaseModelFormSet` directly, since Django's stock admin handles inline pagination differently.

## What is NOT ported

- Unfold Tailwind CSS class constants (`INPUT_CLASSES`, `PROSE_CLASSES`, `BUTTON_CLASSES`, etc.)
- `PaginationFormSetMixin` (unfold-specific inline pagination)
- Unfold-specific JS init files (`select2.init.js`)
- Unfold theme integration or color system
- Template-only contrib modules (guardian, simple_history, location_field, constance) — the standard admin works with these libraries out of the box

## Usage

```python
# settings.py
INSTALLED_APPS = [
    "django_admin_boost.admin",                      # required base
    "django_admin_boost.admin.contrib.filters",      # optional
    "django_admin_boost.admin.contrib.inlines",      # optional
    "django_admin_boost.admin.contrib.forms",        # optional
]

# admin.py — filters
from django_admin_boost.admin.contrib.filters.admin import (
    RangeDateFilter,
    SliderNumericFilter,
    TextFilter,
)

class MyModelAdmin(admin.ModelAdmin):
    list_filter = [
        ("price", SliderNumericFilter),
        ("created", RangeDateFilter),
        TextFilter,
    ]

# admin.py — non-related inlines
from django_admin_boost.admin.contrib.inlines.admin import NonrelatedStackedInline

class TagInline(NonrelatedStackedInline):
    model = Tag

    def get_form_queryset(self, obj):
        return Tag.objects.filter(items__pk=obj.pk)

    def save_new_instance(self, parent, instance):
        instance.save()
        parent.tags.add(instance)

# admin.py — widgets
from django_admin_boost.admin.contrib.forms.widgets import ArrayWidget, WysiwygWidget
```

## Public API

### filters

All filter classes exported from `django_admin_boost.admin.contrib.filters.admin`:

- `TextFilter`, `FieldTextFilter`
- `RadioFilter`, `CheckboxFilter`, `ChoicesRadioFilter`, `ChoicesCheckboxFilter`, `BooleanRadioFilter`, `RelatedCheckboxFilter`, `AllValuesCheckboxFilter`
- `RangeDateFilter`, `RangeDateTimeFilter`
- `SingleNumericFilter`, `RangeNumericFilter`, `RangeNumericListFilter`, `SliderNumericFilter`
- `DropdownFilter`, `MultipleDropdownFilter`, `ChoicesDropdownFilter`, `MultipleChoicesDropdownFilter`, `RelatedDropdownFilter`, `MultipleRelatedDropdownFilter`
- `AutocompleteSelectFilter`, `AutocompleteSelectMultipleFilter`

### inlines

Exported from `django_admin_boost.admin.contrib.inlines.admin`:

- `NonrelatedInlineMixin`
- `NonrelatedStackedInline`
- `NonrelatedTabularInline`

### forms

Exported from `django_admin_boost.admin.contrib.forms.widgets`:

- `ArrayWidget`
- `WysiwygWidget`
