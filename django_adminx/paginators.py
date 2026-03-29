"""Performance-oriented paginator for Django admin."""

from __future__ import annotations

from django.core.paginator import Paginator
from django.db import connections
from django.db.models import QuerySet
from django.utils.functional import cached_property


class EstimatedCountPaginator(Paginator):
    """
    Paginator that uses PostgreSQL's ``pg_class.reltuples`` for fast row
    estimates on unfiltered querysets.

    On large tables the default ``COUNT(*)`` can be extremely slow.  PostgreSQL
    maintains a row-count estimate in the ``pg_class`` catalogue table that is
    updated by ``VACUUM`` and ``ANALYZE``.  This paginator reads that estimate
    when it is safe to do so and falls back to a real ``COUNT(*)`` otherwise.

    Fallback conditions (any one triggers a real count):
    * The database backend is not PostgreSQL.
    * The queryset has WHERE clauses (i.e. admin filters are active).
    * The estimate is ≤ 0 (table freshly created / never analysed).
    """

    @cached_property
    def count(self) -> int:  # type: ignore[override]
        """Return the total number of objects, using an estimate when possible."""
        queryset = self.object_list

        if not isinstance(queryset, QuerySet):
            return len(queryset)  # type: ignore[arg-type]

        if self._can_use_estimate(queryset):
            estimate = self._get_estimate(queryset)
            if estimate is not None and estimate > 0:
                return int(estimate)

        return queryset.count()

    def _can_use_estimate(self, queryset: QuerySet) -> bool:  # type: ignore[type-arg]
        """Return True if we can safely use pg_class.reltuples."""
        connection = connections[queryset.db]
        if connection.vendor != "postgresql":
            return False

        # Check for WHERE clauses — if the queryset is filtered, the estimate
        # would be inaccurate.
        return not queryset.query.where

    def _get_estimate(self, queryset: QuerySet) -> float | None:  # type: ignore[type-arg]
        """Read the row-count estimate from pg_class.reltuples."""
        table_name = queryset.query.model._meta.db_table  # type: ignore[union-attr]  # noqa: SLF001
        connection = connections[queryset.db]

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT reltuples FROM pg_class WHERE relname = %s",
                [table_name],
            )
            row = cursor.fetchone()

        if row is None:
            return None
        return row[0]
