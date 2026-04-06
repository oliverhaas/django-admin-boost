"""Performance-oriented ModelAdmin mixins."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Count

from django_admin_boost.paginators import EstimatedCountPaginator

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest

_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)


class ListFieldsMixin:
    """
    ModelAdmin mixin that optimises changelist querysets by limiting fetched columns.

    Three modes of operation:

    1. **Explicit whitelist** — set ``list_only_fields`` to a list of field names.
       The queryset will use ``.only(pk, *list_only_fields)``.
       An empty list means ``.only(pk)``.

    2. **Explicit blacklist** — set ``list_defer_fields`` to a list of field names.
       The queryset will use ``.defer(*list_defer_fields)``.
       An empty list disables the optimisation entirely (opt-out escape hatch).

    3. **Auto mode** (default) — when neither attribute is set, ``list_display``
       is inspected to determine which concrete model fields are needed, and
       ``.only(pk, *resolved_fields)`` is applied.

    Setting both ``list_only_fields`` and ``list_defer_fields`` raises
    ``ImproperlyConfigured``.

    The optimisation is only applied on changelist requests; add/change views
    always get the full queryset.

    Example::

        class BookAdmin(ListFieldsMixin, admin.ModelAdmin):
            list_only_fields = ["id", "title", "status", "created_at"]
    """

    list_only_fields: list[str] | None = None
    list_defer_fields: list[str] | None = None

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs: QuerySet[Any] = super().get_queryset(request)  # type: ignore[misc]

        if not self._is_changelist_request(request):
            return qs

        if self.list_only_fields is not None and self.list_defer_fields is not None:
            raise ImproperlyConfigured(
                f"Cannot set both list_only_fields and list_defer_fields on "
                f"{self.__class__.__name__}. Use one or the other.",
            )

        # Apply M2M count annotations before field filtering
        m2m_annotations = self._resolve_m2m_annotations()
        if m2m_annotations:
            qs = qs.annotate(**m2m_annotations)

        if self.list_only_fields is not None:
            pk_name = self.opts.pk.name  # type: ignore[attr-defined]
            fields = {pk_name, *self.list_only_fields}
            return qs.only(*fields)

        if self.list_defer_fields is not None:
            if not self.list_defer_fields:
                return qs  # empty list = opt-out
            return qs.defer(*self.list_defer_fields)

        # Auto mode: resolve list_display to concrete fields
        fields = self._resolve_list_display_fields()
        return qs.only(*fields)

    def get_list_display(self, request: HttpRequest) -> list[object]:
        # super().get_list_display() may not exist when mixin is used standalone;
        # fall back to self.list_display which BaseModelAdmin/ModelAdmin provide.
        parent = super()
        if hasattr(parent, "get_list_display"):
            list_display = list(parent.get_list_display(request))  # type: ignore[misc]
        else:
            list_display = list(self.list_display)  # type: ignore[attr-defined]
        m2m_annotations = self._resolve_m2m_annotations()
        for entry in list(list_display):
            annotation_name = f"{entry}_count"
            if annotation_name in m2m_annotations:
                idx = list_display.index(entry)

                def make_count_display(field_name: str, ann_name: str) -> object:
                    def count_display(obj: object) -> object:
                        return getattr(obj, ann_name, 0)

                    count_display.short_description = field_name.replace("_", " ").title()  # type: ignore[attr-defined]
                    count_display.admin_order_field = ann_name  # type: ignore[attr-defined]
                    return count_display

                list_display[idx] = make_count_display(entry, annotation_name)
        return list_display

    def _resolve_m2m_annotations(self) -> dict[str, Count]:
        """Detect M2M/reverse FK fields in list_display and return Count annotations."""
        annotations: dict[str, Count] = {}
        for entry in self.list_display:  # type: ignore[attr-defined]
            if not isinstance(entry, str) or entry == "__str__":
                continue
            if callable(getattr(self, entry, None)):
                # Skip if it's a custom callable on the ModelAdmin
                continue
            try:
                field = self.opts.get_field(entry)  # type: ignore[attr-defined]
            except Exception:  # noqa: BLE001, S112
                continue
            if field.many_to_many or field.one_to_many:
                annotation_name = f"{entry}_count"
                annotations[annotation_name] = Count(entry, distinct=True)
        return annotations

    def _resolve_list_display_fields(self) -> set[str]:
        """Resolve ``list_display`` entries to concrete model field names."""
        pk_name = self.opts.pk.name  # type: ignore[attr-defined]
        fields = {pk_name}

        for entry in self.list_display:  # type: ignore[attr-defined]
            if entry == "__str__":
                # __str__ contributes only pk
                continue
            if callable(entry) and not isinstance(entry, str):
                # A callable object (not a string) — skip
                continue
            if isinstance(entry, str):
                # Check if it's a concrete model field
                try:
                    field = self.opts.get_field(entry)  # type: ignore[attr-defined]
                except Exception:  # noqa: BLE001
                    # Not a model field — could be a method on the ModelAdmin
                    # or model. Check if it's a method on self.
                    if hasattr(self, entry) and callable(getattr(self, entry)):
                        continue
                    # Could be a model method/property — skip
                    continue
                # For ForeignKey fields, Django stores the _id column
                if hasattr(field, "attname"):
                    fields.add(field.attname)
                else:
                    fields.add(entry)

        return fields

    def _is_changelist_request(self, request: HttpRequest) -> bool:
        """Return True when *request* targets the changelist (not add/change)."""
        resolver = getattr(request, "resolver_match", None)
        if resolver is not None:
            url_name: str = resolver.url_name or ""
            return url_name.endswith("_changelist")

        path = request.path
        if path.endswith(("/add/", "/change/")):
            return False
        parts = [p for p in path.rstrip("/").split("/") if p]
        if parts:
            last = parts[-1]
            if last.isdigit() or _UUID_RE.match(last):
                return False
        return True


class SmartPaginatorMixin:
    """
    ModelAdmin mixin that uses :class:`~django_admin_boost.paginators.EstimatedCountPaginator`.

    On PostgreSQL this avoids expensive ``COUNT(*)`` queries for unfiltered
    changelist views by reading the row estimate from ``pg_class.reltuples``.

    ``show_full_result_count`` is set to ``False`` because the count is an
    estimate and displaying "1000 results (1000 total)" would be misleading.
    """

    paginator: type[EstimatedCountPaginator] = EstimatedCountPaginator
    show_full_result_count = False
