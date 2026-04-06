"""Dashboard widget system for the boost admin index page."""

from __future__ import annotations

from typing import Any

from django.http import HttpRequest


class Widget:
    """Base dashboard widget. Subclass and override get_context()."""

    template_name: str = "boost/widgets/base.html"
    htmx: bool = False

    def get_context(self, request: HttpRequest) -> dict[str, Any]:
        raise NotImplementedError


class ValueWidget(Widget):
    """Single KPI value — e.g. 'Total Users: 1,234'."""

    template_name = "boost/widgets/value.html"

    def __init__(
        self,
        label: str,
        value: Any,
        icon: str = "",
        description: str = "",
        **kwargs: Any,
    ) -> None:
        self.label = label
        self._value = value
        self.icon = icon
        self.description = description
        self.htmx = kwargs.get("htmx", False)

    def get_context(self, request: HttpRequest) -> dict[str, Any]:
        value = self._value(request) if callable(self._value) else self._value
        return {
            "label": self.label,
            "value": value,
            "icon": self.icon,
            "description": self.description,
        }


class TableWidget(Widget):
    """Small data table — e.g. recent orders."""

    template_name = "boost/widgets/table.html"

    def __init__(
        self,
        title: str,
        headers: list[str],
        rows: Any,
        **kwargs: Any,
    ) -> None:
        self.title = title
        self.headers = headers
        self._rows = rows
        self.htmx = kwargs.get("htmx", False)

    def get_context(self, request: HttpRequest) -> dict[str, Any]:
        rows = self._rows(request) if callable(self._rows) else self._rows
        return {
            "title": self.title,
            "headers": self.headers,
            "rows": rows,
        }


class ChartWidget(Widget):
    """Chart.js chart. Lazy-loaded via HTMX by default."""

    template_name = "boost/widgets/chart.html"
    htmx = True

    def __init__(
        self,
        title: str,
        chart_type: str,
        data: Any,
        **kwargs: Any,
    ) -> None:
        self.title = title
        self.chart_type = chart_type
        self._data = data
        self.htmx = kwargs.get("htmx", True)

    def get_context(self, request: HttpRequest) -> dict[str, Any]:
        data = self._data(request) if callable(self._data) else self._data
        return {
            "title": self.title,
            "chart_type": self.chart_type,
            "data": data,
        }


class RecentActionsWidget(Widget):
    """Drop-in replacement for Django's recent actions sidebar."""

    template_name = "boost/widgets/recent_actions.html"

    def __init__(self, limit: int = 10, **kwargs: Any) -> None:
        self.limit = limit
        self.htmx = kwargs.get("htmx", False)

    def get_context(self, request: HttpRequest) -> dict[str, Any]:
        from django_admin_boost.admin.models import LogEntry

        qs = LogEntry.objects.select_related("content_type", "user")
        if not getattr(request.user, "is_anonymous", True):
            qs = qs.filter(user=request.user)  # type: ignore[misc]
        return {
            "entries": list(qs[: self.limit]),
            "limit": self.limit,
        }
