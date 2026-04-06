"""Boost admin site with dashboard widget support."""

from __future__ import annotations

from typing import Any

from django.contrib.admin import AdminSite
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse


class BoostAdminSite(AdminSite):
    """Admin site with dashboard widget grid on the index page."""

    # Dashboard widget rows — list of lists of Widget instances
    dashboard_widgets: list[list] = []

    def index(  # type: ignore[override]
        self,
        request: HttpRequest,
        extra_context: dict | None = None,
    ) -> HttpResponse:
        extra_context = extra_context or {}
        extra_context["dashboard_widgets"] = self._get_dashboard_widgets(request)
        return super().index(request, extra_context=extra_context)

    def _get_dashboard_widgets(self, request: HttpRequest) -> list[list[dict[str, Any]]]:
        """Resolve widget rows into context dicts for rendering."""
        rows = []
        for row in self.dashboard_widgets:
            rendered_row = []
            for widget in row:
                rendered_row.append(
                    {
                        "template_name": widget.template_name,
                        "htmx": widget.htmx,
                        "context": widget.get_context(request) if not widget.htmx else {},
                        "widget_id": id(widget),
                    },
                )
            rows.append(rendered_row)
        return rows

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path(
                "boost/widget/<int:widget_id>/",
                self.admin_view(self.widget_view),
                name="boost_widget",
            ),
        ]
        return custom_urls + urls

    def widget_view(self, request: HttpRequest, widget_id: int) -> HttpResponse:
        """HTMX endpoint for lazy-loaded dashboard widgets."""
        for row in self.dashboard_widgets:
            for widget in row:
                if id(widget) == widget_id:
                    context = widget.get_context(request)
                    return TemplateResponse(request, widget.template_name, context)
        return HttpResponse(status=404)
