"""Toy admin registrations for the unmanaged kernel smoke tests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Self

from django.contrib import admin

from django_admin_boost.unmanaged import UnmanagedModelAdmin, UnmanagedQuerySet

from .models import CacheEntry

if TYPE_CHECKING:
    from collections.abc import Iterator

    from django.db.models import Model
    from django.http import HttpRequest, HttpResponse


_DATA: list[CacheEntry] = [
    CacheEntry(key="alpha", value="one", hits=1),
    CacheEntry(key="beta", value="two", hits=2),
    CacheEntry(key="gamma", value="three", hits=3),
]


class ListUnmanagedQuerySet(UnmanagedQuerySet):
    """Tiny list-backed UnmanagedQuerySet used by the smoke test."""

    def __init__(self, model: type[Model], items: list[Any]) -> None:
        super().__init__(model)
        self._items = items

    def count(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._items)

    def __getitem__(self, key: int | slice) -> Any:
        return self._items[key]

    def filter(self, *args: Any, pk__in: list[Any] | None = None, **kwargs: Any) -> Self:
        if pk__in is None:
            return self
        return type(self)(self.model, [x for x in self._items if x.pk in pk__in])

    def order_by(self, *fields: str) -> Self:
        return self


@admin.register(CacheEntry)
class CacheAdmin(UnmanagedModelAdmin):
    """Read-only admin over the in-memory ``_DATA`` list."""

    list_display: ClassVar[list[str]] = ["key", "value", "hits"]
    extra_changelist_params: ClassVar[tuple[str, ...]] = ("cursor",)
    captured_params: ClassVar[dict[str, str]] = {}

    def has_view_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return True

    def get_queryset(self, request: HttpRequest) -> ListUnmanagedQuerySet:
        return ListUnmanagedQuerySet(CacheEntry, _DATA)

    def changelist_view(
        self,
        request: HttpRequest,
        extra_context: dict[str, Any] | None = None,
    ) -> HttpResponse:
        response = super().changelist_view(request, extra_context=extra_context)
        type(self).captured_params = dict(getattr(request, "_unmanaged_params", {}))
        return response
