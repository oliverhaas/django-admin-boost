from __future__ import annotations

import datetime

from django.conf import settings


def parse_date_str(value: str) -> datetime.date | None:
    """Parse a date string using Django's DATE_INPUT_FORMATS."""
    for fmt in settings.DATE_INPUT_FORMATS:
        try:
            return datetime.datetime.strptime(value, fmt).date()
        except (ValueError, TypeError):
            continue
    return None


def parse_datetime_str(value: str) -> datetime.datetime | None:
    """Parse a datetime string using Django's DATETIME_INPUT_FORMATS."""
    for fmt in settings.DATETIME_INPUT_FORMATS:
        try:
            return datetime.datetime.strptime(value, fmt)
        except (ValueError, TypeError):
            continue
    return None
