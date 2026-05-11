"""Read-only admin over an in-memory recent-search log.

Demonstrates ``django_admin_boost.unmanaged`` — building a Django admin page over
data that doesn't live in the relational database. Here the "data" is a
hand-populated list of search terms; in a real app the source would be a Redis
sorted set, a cache backend, or a third-party search service like Algolia or
Meilisearch.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Self

from django.contrib import admin
from django.db import models
from django.http import HttpRequest

from django_admin_boost.unmanaged import (
    UnmanagedModel,
    UnmanagedModelAdmin,
    UnmanagedModelMeta,
    UnmanagedQuerySet,
)


# Seeded log — pretend this lives in Redis or a cache backend.
_NOW = datetime.now(timezone.utc)
_LOG: list[dict[str, Any]] = [
    {"term": "wireless headphones", "count": 142, "last_at": _NOW - timedelta(minutes=3)},
    {"term": "ergonomic keyboard", "count": 89, "last_at": _NOW - timedelta(minutes=12)},
    {"term": "standing desk", "count": 67, "last_at": _NOW - timedelta(minutes=27)},
    {"term": "monitor 4k", "count": 54, "last_at": _NOW - timedelta(hours=1)},
    {"term": "usb-c hub", "count": 41, "last_at": _NOW - timedelta(hours=2)},
    {"term": "laptop sleeve", "count": 22, "last_at": _NOW - timedelta(hours=4)},
    {"term": "noise cancelling", "count": 19, "last_at": _NOW - timedelta(hours=6)},
    {"term": "webcam", "count": 12, "last_at": _NOW - timedelta(hours=8)},
]


class RecentSearch(UnmanagedModel):
    """A search-term tally backed by an in-memory log, not the database."""

    term = models.CharField(max_length=200, primary_key=True)
    count = models.IntegerField(default=0)
    last_at = models.DateTimeField()

    class Meta(UnmanagedModelMeta):
        app_label = "catalog"
        verbose_name = "recent search"
        verbose_name_plural = "recent searches"

    def __str__(self) -> str:
        return self.term


class RecentSearchQuerySet(UnmanagedQuerySet):
    """List-backed queryset over the in-memory log."""

    def __init__(self, model: type[RecentSearch], log: list[dict[str, Any]]) -> None:
        super().__init__(model)
        self._rows = [RecentSearch(term=r["term"], count=r["count"], last_at=r["last_at"]) for r in log]

    def count(self) -> int:
        return len(self._rows)

    def __iter__(self):
        return iter(self._rows)

    def __getitem__(self, key: int | slice) -> Any:
        return self._rows[key]

    def filter(self, *args: Any, pk__in: list[Any] | None = None, **kwargs: Any) -> Self:
        if pk__in is None:
            return self
        keep = [{"term": r.term, "count": r.count, "last_at": r.last_at} for r in self._rows if r.pk in pk__in]
        return type(self)(self.model, keep)

    def order_by(self, *fields: str) -> Self:
        return self


@admin.register(RecentSearch)
class RecentSearchAdmin(UnmanagedModelAdmin):
    """Read-only admin for the recent-searches in-memory log."""

    list_display = ["term", "count", "last_at"]
    disable_list_pagination = True

    def has_view_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return request.user.is_staff

    def get_queryset(self, request: HttpRequest) -> RecentSearchQuerySet:
        # Sort newest-first. In a real app you'd sort in the data layer.
        sorted_log = sorted(_LOG, key=lambda r: r["last_at"], reverse=True)
        return RecentSearchQuerySet(RecentSearch, sorted_log)
