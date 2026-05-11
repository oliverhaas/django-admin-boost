"""Toy unmanaged models used by tests of the unmanaged kernel."""

from __future__ import annotations

from django.db import models

from django_admin_boost.unmanaged import UnmanagedModel, UnmanagedModelMeta


class Thing(UnmanagedModel):
    """Bare-bones unmanaged model — used for Meta/save/delete/register/__str__ tests."""

    key = models.CharField(max_length=200, primary_key=True)
    label = models.CharField(max_length=200, default="")

    class Meta(UnmanagedModelMeta):
        app_label = "unmanagedapp"


class CacheEntry(UnmanagedModel):
    """Toy cache-entry model — used for the end-to-end changelist smoke test."""

    key = models.CharField(max_length=200, primary_key=True)
    value = models.CharField(max_length=200)
    hits = models.IntegerField(default=0)

    class Meta(UnmanagedModelMeta):
        app_label = "unmanagedapp"
        verbose_name = "cache entry"
        verbose_name_plural = "cache entries"

    def __str__(self) -> str:
        return self.key
