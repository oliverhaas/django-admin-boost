"""Performance-oriented ModelAdmin mixins."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django_adminx.paginators import EstimatedCountPaginator

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


class ListOnlyFieldsMixin:
    """
    ModelAdmin mixin that applies `.only()` to changelist querysets.

    Set ``list_only_fields`` to a list of field names that the list view needs.
    On changelist requests the queryset will be narrowed with ``.only(*list_only_fields)``,
    reducing the number of columns fetched from the database.

    The optimisation is skipped for add/change views so that all fields remain
    available for editing.

    Example::

        class BookAdmin(ListOnlyFieldsMixin, admin.ModelAdmin):
            list_only_fields = ["id", "title", "status", "created_at"]
    """

    list_only_fields: list[str] | None = None

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs: QuerySet[Any] = super().get_queryset(request)  # type: ignore[misc]

        if self.list_only_fields and self._is_changelist_request(request):
            qs = qs.only(*self.list_only_fields)

        return qs

    def _is_changelist_request(self, request: HttpRequest) -> bool:
        """Return True when *request* targets the changelist (not add/change)."""
        # The resolver_match is set by Django's URL dispatcher. For the
        # changelist the url name ends with ``_changelist``.  Add and change
        # views use ``_add`` and ``_change`` respectively.
        resolver = getattr(request, "resolver_match", None)
        if resolver is not None:
            url_name: str = resolver.url_name or ""
            return url_name.endswith("_changelist")

        # Fallback: inspect the path.  Changelist lives at the model root URL
        # (e.g. /admin/app/model/), while change views contain an object PK
        # segment and add views end with ``/add/``.
        path = request.path
        if path.endswith(("/add/", "/change/")):
            return False
        # A path ending with "/<pk>/" is a change view — check for a numeric
        # or UUID-ish last segment.
        parts = [p for p in path.rstrip("/").split("/") if p]
        if parts:
            last = parts[-1]
            # If the last segment looks like a PK (digits or UUID), it's a
            # change view.
            if last.isdigit():
                return False
        return True


class SmartPaginatorMixin:
    """
    ModelAdmin mixin that uses :class:`~django_adminx.paginators.EstimatedCountPaginator`.

    On PostgreSQL this avoids expensive ``COUNT(*)`` queries for unfiltered
    changelist views by reading the row estimate from ``pg_class.reltuples``.

    ``show_full_result_count`` is set to ``False`` because the count is an
    estimate and displaying "1000 results (1000 total)" would be misleading.
    """

    paginator: type[EstimatedCountPaginator] = EstimatedCountPaginator
    show_full_result_count = False
