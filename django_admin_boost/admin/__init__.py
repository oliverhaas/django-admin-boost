"""django-admin-boost: Django admin with Jinja2 support and performance optimizations.

Subclasses ``django.contrib.admin`` — adds Jinja2 template support,
``ListFieldsMixin``, ``SmartPaginatorMixin``, and ``EstimatedCountPaginator``.

Usage::

    INSTALLED_APPS = ["django_admin_boost.admin", ...]

    # in your admin.py — use exactly like django.contrib.admin:
    from django_admin_boost.admin import admin

    @admin.register(MyModel)
    class MyModelAdmin(admin.ModelAdmin):
        ...
"""

from django.contrib.admin import (
    HORIZONTAL,
    VERTICAL,
    AdminSite,
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
    autodiscover,
    display,
    register,
    site,
)
from django.contrib.admin import ModelAdmin as DjangoModelAdmin
from django.contrib.admin import StackedInline as DjangoStackedInline
from django.contrib.admin import TabularInline as DjangoTabularInline

from django_admin_boost.mixins import ListFieldsMixin, SmartPaginatorMixin
from django_admin_boost.paginators import EstimatedCountPaginator


class ModelAdmin(SmartPaginatorMixin, ListFieldsMixin, DjangoModelAdmin):
    """ModelAdmin with performance optimizations baked in."""


class StackedInline(SmartPaginatorMixin, ListFieldsMixin, DjangoStackedInline):
    """StackedInline with performance optimizations baked in."""


class TabularInline(SmartPaginatorMixin, ListFieldsMixin, DjangoTabularInline):
    """TabularInline with performance optimizations baked in."""


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
