"""QuerySet-shaped wrappers for data sources that don't live in the database."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Self

if TYPE_CHECKING:
    from collections.abc import Iterator

    from django.db.models import Model


class _FakeQuery:
    """Minimal stand-in for :class:`django.db.models.sql.Query`.

    Django's admin :class:`~django.contrib.admin.views.main.ChangeList` reads
    ``queryset.query.select_related`` and ``queryset.query.order_by`` directly;
    a few internal call sites also probe ``query.where``. This stub exposes
    those attributes with safe defaults so an :class:`UnmanagedQuerySet` can
    sail through the protocol checks.
    """

    select_related: bool = False
    order_by: tuple[str, ...] = ()
    where: tuple[Any, ...] = ()

    def __init__(self, model: type[Model]) -> None:
        self.model = model


class UnmanagedQuerySet:
    """Abstract base for QuerySet-shaped wrappers around non-DB data sources.

    Subclasses MUST implement :meth:`count`, :meth:`__iter__`,
    :meth:`__getitem__`, :meth:`filter`, and :meth:`order_by`. Everything else
    on this class is a safe no-op default that satisfies the bits of the
    QuerySet protocol that :class:`~django.contrib.admin.views.main.ChangeList`
    and :class:`~django.core.paginator.Paginator` poke at.

    Subclasses do not need to call ``super().__init__()`` unless they want the
    default ``self.model`` / ``self.query`` wiring.
    """

    ordered: ClassVar[bool] = True
    db: ClassVar[str] = "default"

    def __init__(self, model: type[Model]) -> None:
        self.model = model
        self.query = _FakeQuery(model)

    # --- abstract: subclasses MUST override ----------------------------------

    def count(self) -> int:
        raise NotImplementedError

    def __iter__(self) -> Iterator[Any]:
        raise NotImplementedError

    def __getitem__(self, key: int | slice) -> Any:
        raise NotImplementedError

    def filter(self, *args: Any, **kwargs: Any) -> Self:
        raise NotImplementedError

    def order_by(self, *fields: str) -> Self:
        raise NotImplementedError

    # --- concrete defaults the protocol demands ------------------------------

    def __len__(self) -> int:
        return self.count()

    def __bool__(self) -> bool:
        return self.count() > 0

    def all(self) -> Self:
        return self

    def select_related(self, *fields: str) -> Self:
        return self

    def distinct(self, *fields: str) -> Self:
        return self

    def alias(self, *args: Any, **kwargs: Any) -> Self:
        return self

    def only(self, *fields: str) -> Self:
        return self

    def defer(self, *fields: str) -> Self:
        return self

    def _clone(self) -> Self:
        return self

    def _next_is_sticky(self) -> Self:
        return self

    def none(self) -> Self:
        raise NotImplementedError
