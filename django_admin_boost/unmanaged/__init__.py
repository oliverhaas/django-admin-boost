"""Thin kernel for Django admin pages backed by non-DB data.

Three abstract base classes — :class:`UnmanagedModel`,
:class:`UnmanagedQuerySet`, and :class:`UnmanagedModelAdmin` — that let
consumers build admin pages over caches, in-memory state, third-party APIs,
or anything else that isn't a real database table.

This module is not a Django app; install it inside your own AppConfig.
"""

from django_admin_boost.unmanaged.admin import UnmanagedModelAdmin
from django_admin_boost.unmanaged.models import UnmanagedModel, UnmanagedModelError, UnmanagedModelMeta
from django_admin_boost.unmanaged.querysets import UnmanagedQuerySet

__all__ = [
    "UnmanagedModel",
    "UnmanagedModelAdmin",
    "UnmanagedModelError",
    "UnmanagedModelMeta",
    "UnmanagedQuerySet",
]
