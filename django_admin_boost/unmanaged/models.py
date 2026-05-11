"""Model base for entities whose data lives outside the relational database."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from django.contrib import admin as django_admin
from django.db import models
from django.db.utils import NotSupportedError

if TYPE_CHECKING:
    from django.contrib.admin import AdminSite

    from django_admin_boost.unmanaged.admin import UnmanagedModelAdmin


class UnmanagedModelError(NotSupportedError):
    """Raised when an operation isn't valid on an unmanaged model."""


class UnmanagedModelMeta:
    """Mix into a model's ``Meta`` to lock ``managed = False`` for free.

    :class:`~django.db.models.options.Options` resolves Meta attributes by
    walking the MRO of the inner ``Meta`` class, so inheriting from this
    sentinel is sufficient to inject ``managed = False`` without any
    metaclass gymnastics.
    """

    managed: ClassVar[bool] = False
    abstract: ClassVar[bool] = False


class UnmanagedModel(models.Model):
    """Abstract base for models whose data doesn't live in the database.

    Subclasses must set ``app_label`` on their inner ``Meta`` (concrete
    unmanaged models declared outside ``INSTALLED_APPS`` would otherwise
    raise ``RuntimeError`` from :class:`~django.db.models.base.ModelBase`).

    Example::

        class CacheEntry(UnmanagedModel):
            key = models.CharField(max_length=200, primary_key=True)

            class Meta(UnmanagedModelMeta):
                app_label = "mycache"
    """

    class Meta(UnmanagedModelMeta):
        abstract = True

    def __str__(self) -> str:
        return str(self.pk)

    def save(self, *args: Any, **kwargs: Any) -> None:
        raise UnmanagedModelError(
            f"{type(self).__name__} is an unmanaged model and cannot be saved.",
        )

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        raise UnmanagedModelError(
            f"{type(self).__name__} is an unmanaged model and cannot be deleted.",
        )

    @classmethod
    def register(
        cls,
        admin_cls: type[UnmanagedModelAdmin],
        site: AdminSite | None = None,
    ) -> None:
        """Register *admin_cls* for this model on *site* (defaults to ``admin.site``)."""
        target = site if site is not None else django_admin.site
        target.register(cls, admin_cls)
