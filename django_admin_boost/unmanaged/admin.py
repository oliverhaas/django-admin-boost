"""ModelAdmin base for unmanaged models."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from django.contrib import admin
from django.core.paginator import Paginator

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

    from django_admin_boost.unmanaged.querysets import UnmanagedQuerySet


class _SinglePagePaginator(Paginator):
    """Paginator that reports a single page; suppresses changelist pagination chrome."""

    @property
    def num_pages(self) -> int:
        return 1


class UnmanagedModelAdmin(admin.ModelAdmin):
    """ModelAdmin for models whose changelist is backed by an :class:`UnmanagedQuerySet`.

    Defaults are read-only: no add/change/delete permissions, no
    ``delete_selected`` action. Override the permission hooks or
    :meth:`has_view_permission` to opt in. Subclasses must implement
    :meth:`get_queryset` to return an :class:`UnmanagedQuerySet`.
    """

    actions = []  # noqa: RUF012
    list_per_page: ClassVar[int] = 100

    extra_changelist_params: ClassVar[tuple[str, ...]] = ()
    """GET parameter names to pop off ``request.GET`` before ChangeList sees them.

    Without this hook, ChangeList raises ``IncorrectLookupParameters`` for any
    GET key that isn't a recognised field lookup. The popped values land on
    ``request._unmanaged_params`` as ``dict[str, str]``.
    """

    disable_list_pagination: ClassVar[bool] = False
    """When True, suppress pagination chrome by using a single-page paginator."""

    # --- read-only by default -----------------------------------------------

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False

    # --- subclass hooks ------------------------------------------------------

    def get_queryset(self, request: HttpRequest) -> UnmanagedQuerySet:  # type: ignore[override]
        raise NotImplementedError(
            f"{type(self).__name__} must override get_queryset() to return an UnmanagedQuerySet.",
        )

    # --- bake-ins ------------------------------------------------------------

    def get_actions(self, request: HttpRequest) -> dict[str, Any]:
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions

    def get_paginator(
        self,
        request: HttpRequest,
        queryset: Any,
        per_page: int,
        orphans: int = 0,
        allow_empty_first_page: bool = True,
    ) -> Paginator:
        cls = _SinglePagePaginator if self.disable_list_pagination else self.paginator
        return cls(queryset, per_page, orphans, allow_empty_first_page)

    def changelist_view(
        self,
        request: HttpRequest,
        extra_context: dict[str, Any] | None = None,
    ) -> HttpResponse:
        if self.extra_changelist_params:
            self._strip_extra_params(request)
        return super().changelist_view(request, extra_context=extra_context)

    def _strip_extra_params(self, request: HttpRequest) -> None:
        """Pop ``extra_changelist_params`` off ``request.GET`` onto ``request._unmanaged_params``."""
        mutable = request.GET.copy()
        stash: dict[str, str] = {}
        for name in self.extra_changelist_params:
            if name in mutable:
                values = mutable.pop(name)
                stash[name] = values[-1]
        request.GET = mutable  # type: ignore[assignment]
        request._unmanaged_params = stash  # type: ignore[attr-defined]
