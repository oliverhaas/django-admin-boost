"""Jinja2 environment factory for boost admin templates."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from urllib.parse import quote

import jinja2
from django.contrib.admin.models import LogEntry
from django.contrib.admin.templatetags.admin_list import (
    admin_actions as _raw_admin_actions,
)
from django.contrib.admin.templatetags.admin_list import (
    admin_list_filter as _raw_admin_list_filter,
)
from django.contrib.admin.templatetags.admin_list import (
    date_hierarchy,
    pagination,
    paginator_number,
    result_headers,
    result_hidden_fields,
    result_list,
    results,
    search_form,
)
from django.contrib.admin.templatetags.admin_modify import (
    cell_count,
)
from django.contrib.admin.templatetags.admin_modify import (
    prepopulated_fields_js as _raw_prepopulated_fields_js,
)
from django.contrib.admin.templatetags.admin_modify import (
    submit_row as _raw_submit_row,
)
from django.contrib.admin.templatetags.admin_urls import (
    add_preserved_filters as _raw_add_preserved_filters,
)
from django.templatetags.static import static
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.dateformat import format as dateformat
from django.utils.encoding import iri_to_uri
from django.utils.formats import date_format, localize
from django.utils.html import conditional_escape
from django.utils.text import Truncator, capfirst
from django.utils.translation import get_language, get_language_bidi, gettext, ngettext
from markupsafe import Markup


def environment(**options: object) -> jinja2.Environment:
    """Create a Jinja2 environment configured for boost admin templates."""
    env = jinja2.Environment(**options)  # type: ignore[arg-type]  # noqa: S701
    env.add_extension("jinja2.ext.i18n")

    env.install_gettext_callables(gettext, ngettext, newstyle=True)  # type: ignore[attr-defined]

    env.globals.update(
        {
            "get_current_language": get_language,
            "get_current_language_bidi": get_language_bidi,
            "get_admin_log": _get_admin_log,
            "now": _now,
            "static": static,
            "url": _url,
            "admin_actions": _admin_actions_jinja2,
            "admin_list_filter": _admin_list_filter_safe,
            "date_hierarchy": date_hierarchy,
            "pagination": pagination,
            "paginator_number": paginator_number,
            "result_headers": result_headers,
            "result_hidden_fields": result_hidden_fields,
            "result_list": result_list,
            "results": results,
            "search_form": search_form,
            "prepopulated_fields_js": _prepopulated_fields_js_jinja2,
            "submit_row": _submit_row_jinja2,
            "add_preserved_filters": _add_preserved_filters_jinja2,
        },
    )

    env.filters.update(
        {
            "admin_urlname": _admin_urlname,
            "admin_urlquote": _admin_urlquote,
            "capfirst": _capfirst_safe,
            "iriencode": _iriencode,
            "cell_count": cell_count,
            "date": _date_filter,
            "truncatewords": _truncatewords,
            "unlocalize": _unlocalize,
            "unordered_list": _unordered_list,
            "urlencode_path": _urlencode_path,
            "yesno": _yesno,
        },
    )

    return env


@jinja2.pass_context
def _url(context: Any, viewname: str, *args: object, silent: bool = False, **kwargs: object) -> str:
    try:
        request = context.get("request") if context else None
        current_app = getattr(request, "current_app", None) if request else None
        return reverse(viewname, args=args, kwargs=kwargs, current_app=current_app)
    except NoReverseMatch:
        if silent:
            return ""
        raise


def _now(format_string: str) -> str:
    return dateformat(datetime.now(tz=timezone.get_current_timezone()), format_string)


def _get_admin_log(limit: int = 10, user: object = None) -> object:
    qs = LogEntry.objects.select_related("content_type", "user")
    if user is not None and not getattr(user, "is_anonymous", True):
        qs = qs.filter(user=user)  # type: ignore[misc]
    return qs[:limit]


def _yesno(value: object, arg: str = "yes,no,maybe") -> str:
    bits = arg.split(",")
    if len(bits) < 2:
        return str(value)
    yes, no = bits[0], bits[1]
    maybe = bits[2] if len(bits) > 2 else bits[1]
    if value is None:
        return maybe
    return yes if value else no


def _admin_urlname(value: Any, arg: str) -> str:
    return "admin:%s_%s_%s" % (value.app_label, value.model_name, arg)  # noqa: UP031


def _admin_urlquote(value: object) -> str:
    return quote(str(value))


def _capfirst_safe(value: object) -> str | Markup:
    result = capfirst(str(value)) if value else ""
    if hasattr(value, "__html__"):
        return Markup(result)  # noqa: S704
    return result


def _iriencode(value: str) -> str:
    return iri_to_uri(value)


def _admin_list_filter_safe(cl: Any, spec: Any) -> Markup:
    return Markup(_raw_admin_list_filter(cl, spec))  # noqa: S704


def _jinja2_context_to_dict(context: Any) -> dict[str, Any]:
    if isinstance(context, dict):
        return context
    return dict(context)


@jinja2.pass_context
def _admin_actions_jinja2(context: Any) -> dict[str, Any]:
    return _raw_admin_actions(_jinja2_context_to_dict(context))  # type: ignore[arg-type,return-value]


@jinja2.pass_context
def _submit_row_jinja2(context: Any) -> dict[str, Any]:
    return _raw_submit_row(_jinja2_context_to_dict(context))  # type: ignore[arg-type,return-value]


@jinja2.pass_context
def _prepopulated_fields_js_jinja2(context: Any) -> dict[str, Any]:
    return _raw_prepopulated_fields_js(_jinja2_context_to_dict(context))  # type: ignore[arg-type,return-value]


@jinja2.pass_context
def _add_preserved_filters_jinja2(
    context: Any,
    url: str,
    popup: bool = False,
    to_field: str | None = None,
) -> str:
    return _raw_add_preserved_filters(_jinja2_context_to_dict(context), url, popup, to_field)


def _urlencode_path(value: str) -> str:
    return quote(str(value), safe="/")


def _date_filter(value: Any, arg: str = "DATETIME_FORMAT") -> str:
    if value in (None, ""):
        return ""
    try:
        return date_format(value, arg)
    except AttributeError:
        return ""


def _truncatewords(value: str, arg: int | str = 15) -> str:
    try:
        length = int(arg)
    except (ValueError, TypeError):
        return str(value)
    return Truncator(value).words(length, truncate=" \u2026")


def _unlocalize(value: Any) -> str:
    return str(localize(value, use_l10n=False))


def _unordered_list(value: list[Any]) -> str:
    def _helper(items: list[Any]) -> list[str]:
        output: list[str] = []
        for item in items:
            if isinstance(item, (list, tuple)):
                if output:
                    last = output.pop()
                    last = last.removesuffix("</li>")
                    output.append(last)
                    output.append("<ul>")
                    output.extend(_helper(list(item)))
                    output.append("</ul>")
                    output.append("</li>")
                else:
                    output.append("<ul>")
                    output.extend(_helper(list(item)))
                    output.append("</ul>")
            else:
                output.append(f"<li>{conditional_escape(item)}</li>")
        return output

    return Markup("\n".join(_helper(value)))  # noqa: S704
