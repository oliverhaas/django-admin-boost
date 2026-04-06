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

from django.contrib.admin import (
    HORIZONTAL,
    VERTICAL,
    AllValuesFieldListFilter,
    BooleanFieldListFilter,
    ChoicesFieldListFilter,
    DateFieldListFilter,
    EmptyFieldListFilter,
    FieldListFilter,
    ListFilter,
    RelatedFieldListFilter,
    RelatedOnlyFieldListFilter,
    ShowFacets,
    SimpleListFilter,
    action,
    display,
    register,
)
from django.utils.module_loading import autodiscover_modules

from django_admin_boost.admin import ModelAdmin, StackedInline, TabularInline
from django_admin_boost.boost.sites import BoostAdminSite
from django_admin_boost.mixins import ListFieldsMixin, SmartPaginatorMixin
from django_admin_boost.paginators import EstimatedCountPaginator

site = BoostAdminSite()

__all__ = [
    "HORIZONTAL",
    "VERTICAL",
    "AllValuesFieldListFilter",
    "BooleanFieldListFilter",
    "BoostAdminSite",
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
