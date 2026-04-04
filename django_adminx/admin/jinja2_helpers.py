"""Jinja2 helper utilities for Django admin templates."""

from __future__ import annotations

from typing import Any


def select_admin_template(opts: Any, template_name: str) -> list[str]:  # noqa: ANN401
    """Replicate InclusionAdminNode's 3-level template override hierarchy."""
    return [
        f"admin/{opts.app_label}/{opts.model_name}/{template_name}",
        f"admin/{opts.app_label}/{template_name}",
        f"admin/{template_name}",
    ]
