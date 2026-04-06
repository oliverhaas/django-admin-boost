# Unfold Replacement Design

## Goal

Provide a drop-in replacement for django-unfold at `django_admin_boost.unfold` that uses Jinja2 templates by default with DTL fallback, following the same pattern as the existing `django_admin_boost.admin` replacement.

## Source

django-unfold 0.87.0 (MIT license). All Python, templates, and static assets copied verbatim and adapted.

## Package Structure

```
django_admin_boost/
  unfold/
    __init__.py
    admin.py
    apps.py
    checks.py
    components.py
    dataclasses.py
    datasets.py
    decorators.py
    enums.py
    exceptions.py
    fields.py
    forms.py
    jinja2_env.py
    jinja2_helpers.py
    layout.py
    overrides.py
    paginator.py
    sections.py
    settings.py
    sites.py
    typing.py
    utils.py
    views.py
    widgets.py
    mixins/
      __init__.py
      action_model_admin.py
      base_model_admin.py
      dataset_model_admin.py
      nested_inlines_model_admin.py
    templatetags/
      __init__.py
      unfold.py
      unfold_list.py
    jinja2/          (193 core + 38 contrib templates, converted)
    templates/       (DTL fallback, originals from unfold)
    static/          (copied as-is: Tailwind CSS, Alpine.js, HTMX, Chart.js, fonts)
    contrib/
      __init__.py
      constance/
      filters/
      forms/
      guardian/
      import_export/
      inlines/
      location_field/
      simple_history/
```

## Key Decisions

1. Namespace: `django_admin_boost.unfold`
2. Internal imports rewritten: `unfold.` -> `django_admin_boost.unfold.`
3. Templates converted to Jinja2 via django-jinjafy skill, DTL kept as fallback
4. Static assets copied verbatim
5. Copied Python files excluded from ruff and mypy in pyproject.toml
6. Unfold MIT copyright notice preserved in LICENSES/ directory
7. Tests ported from unfold's 231 tests, plus Jinja2 parity tests

## Usage

```python
INSTALLED_APPS = [
    "django_admin_boost.unfold",
    ...
]

from django_admin_boost.unfold.admin import ModelAdmin
```

## Implementation Steps

1. Copy all unfold Python files, rewrite imports
2. Copy static assets verbatim
3. Copy DTL templates as fallback
4. Convert all templates to Jinja2
5. Create jinja2_env.py and jinja2_helpers.py for unfold template tags
6. Update pyproject.toml (ruff/mypy excludes, hatch build includes)
7. Add LICENSES/UNFOLD-MIT file
8. Port tests
9. Verify everything works
