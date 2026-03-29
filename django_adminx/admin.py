"""Ready-to-use ModelAdmin classes with performance optimisations."""

from __future__ import annotations

from django.contrib.admin import ModelAdmin

from django_adminx.mixins import ListOnlyFieldsMixin, SmartPaginatorMixin


class BaseModelAdmin(SmartPaginatorMixin, ListOnlyFieldsMixin, ModelAdmin):
    """ModelAdmin with all django-adminx performance optimisations applied."""
