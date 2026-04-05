"""django-admin-boost full admin replacement.

Drop-in replacement for ``django.contrib.admin`` with Jinja2 template support
and performance optimizations baked in.

Usage::

    INSTALLED_APPS = ["django_admin_boost.admin", ...]

    # in your admin.py:
    import django_admin_boost.admin as admin

    @admin.register(MyModel)
    class MyModelAdmin(admin.ModelAdmin):
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
from django_admin_boost.admin.sites import AdminSite, site

# Re-export standalone mixins for convenience
from django_admin_boost.mixins import ListFieldsMixin, SmartPaginatorMixin
from django_admin_boost.paginators import EstimatedCountPaginator

__all__ = [
    "HORIZONTAL",
    "VERTICAL",
    "AdminSite",
    "AllValuesFieldListFilter",
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
