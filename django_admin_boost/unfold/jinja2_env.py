"""Jinja2 environment factory for unfold admin templates.

Provides all the globals/filters that unfold's DTL templatetags register,
so that the Jinja2 conversions of those templates render identically.

Usage in settings::

    TEMPLATES = [{
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "APP_DIRS": True,
        "OPTIONS": {
            "environment": "django_admin_boost.unfold.jinja2_env.environment",
            ...
        },
    }]
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from urllib.parse import quote

import jinja2
import jinja2.ext
from django.templatetags.static import static
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.dateformat import format as dateformat
from django.utils.encoding import iri_to_uri
from django.utils.formats import date_format, localize
from django.utils.html import conditional_escape
from django.utils.text import Truncator, capfirst, slugify
from django.utils.translation import get_language, get_language_bidi, gettext, ngettext
from markupsafe import Markup

from django_admin_boost.unfold.jinja2_helpers import select_unfold_template


def environment(**options: object) -> jinja2.Environment:
    """Create a Jinja2 environment configured for unfold admin templates."""
    env = jinja2.Environment(**options)  # type: ignore[arg-type]  # noqa: S701
    env.add_extension("jinja2.ext.i18n")
    env.add_extension(ComponentExtension)
    env.add_extension(CaptureExtension)

    env.install_gettext_callables(gettext, ngettext, newstyle=True)  # type: ignore[attr-defined]

    env.globals.update(
        {
            # Core helpers
            "get_current_language": get_language,
            "get_current_language_bidi": get_language_bidi,
            "now": _now,
            "static": static,
            "url": _url,
            # Template hierarchy helper
            "select_admin_template": select_unfold_template,
            # Unfold templatetag functions (from unfold.py)
            "tab_list": _tab_list_jinja2,
            "action_list": _action_list_jinja2,
            "render_section": _render_section_jinja2,
            "has_nav_item_active": _has_nav_item_active,
            "element_classes": _element_classes_jinja2,
            "fieldset_rows_classes": _fieldset_rows_classes_jinja2,
            "fieldset_row_classes": _fieldset_row_classes_jinja2,
            "fieldset_line_classes": _fieldset_line_classes_jinja2,
            "action_item_classes": _action_item_classes_jinja2,
            "infinite_paginator_url": _infinite_paginator_url,
            "elided_page_range": _elided_page_range,
            "querystring_params": _querystring_params_jinja2,
            "unfold_querystring": _unfold_querystring_jinja2,
            "header_title": _header_title_jinja2,
            "admin_object_app_url": _admin_object_app_url_jinja2,
            "tabs_primary_active": _tabs_primary_active,
            "preserve_filters": _preserve_filters_jinja2,
            # Unfold list templatetag functions (from unfold_list.py)
            "unfold_result_list": _unfold_result_list_jinja2,
            "unfold_search_form": _unfold_search_form_jinja2,
            "unfold_admin_actions": _unfold_admin_actions_jinja2,
            "result_headers": _result_headers,
            "results": _results,
            "result_hidden_fields": _result_hidden_fields,
            "paginator_number": _paginator_number,
        },
    )

    env.filters.update(
        {
            "admin_urlname": _admin_urlname,
            "admin_urlquote": _admin_urlquote,
            "capfirst": _capfirst_safe,
            "iriencode": _iriencode,
            "date": _date_filter,
            "truncatewords": _truncatewords,
            "unlocalize": _unlocalize,
            "unordered_list": _unordered_list,
            "urlencode_path": _urlencode_path,
            "yesno": _yesno,
            "escapejs": _escapejs,
            "linebreaksbr": _linebreaksbr,
            "slugify": _slugify_filter,
            "pluralize": _pluralize,
            # Unfold-specific filters
            "has_active_item": _has_active_item,
            "class_name": _class_name,
            "is_list": _is_list,
            "index": _index,
            "tabs": _tabs,
            "changeform_data": _changeform_data,
            "changeform_condition": _changeform_condition,
            "has_nested_tables": _has_nested_tables,
            "inline_add_button_text": _inline_add_button_text,
            "add_css_class": _add_css_class,
            "tabs_active": _tabs_active,
            "tabs_errors_count": _tabs_errors_count,
            "unicoded_slugify": _unicoded_slugify,
        },
    )

    return env


# ---------------------------------------------------------------------------
# Jinja2 Extensions for {% component %} and {% capture %}
# ---------------------------------------------------------------------------


class ComponentExtension(jinja2.ext.Extension):
    """Jinja2 extension for {% component "template" with key=val %}...{% endcomponent %}."""

    tags = {"component"}

    def parse(self, parser: jinja2.ext.Extension) -> jinja2.nodes.Node:
        lineno = next(parser.stream).lineno
        # Parse template name
        template_name = parser.parse_expression()
        # Parse optional 'with key=val' pairs
        kwargs = []
        if parser.stream.current.test("name:with"):
            next(parser.stream)
            while not parser.stream.current.test("block_end"):
                if kwargs:
                    parser.stream.expect("comma") if parser.stream.current.test("comma") else None
                key = parser.stream.expect("name").value
                parser.stream.expect("assign")
                value = parser.parse_expression()
                kwargs.append(jinja2.nodes.Keyword(key, value, lineno=lineno))

        # Check for include_context flag
        include_context = False
        if parser.stream.current.test("name:include_context"):
            next(parser.stream)
            include_context = True

        body = parser.parse_statements(["name:endcomponent"], drop_needle=True)

        return jinja2.nodes.CallBlock(
            self.call_method(
                "_render_component",
                [template_name, jinja2.nodes.Const(include_context)],
                kwargs,
            ),
            [],
            [],
            body,
        ).set_lineno(lineno)

    def _render_component(
        self,
        template_name: str,
        include_context: bool,
        caller: Any,
        **kwargs: Any,
    ) -> str:
        children = caller()
        ctx = {"children": children, **kwargs} if children.strip() else {**kwargs}
        tmpl = self.environment.get_template(template_name)
        return tmpl.render(ctx)


class CaptureExtension(jinja2.ext.Extension):
    """Jinja2 extension for {% capture as varname silent %}...{% endcapture %}."""

    tags = {"capture"}

    def parse(self, parser: jinja2.ext.Extension) -> jinja2.nodes.Node:
        lineno = next(parser.stream).lineno

        # Parse optional 'as varname'
        var_name = None
        silent = False
        if parser.stream.current.test("name:as"):
            next(parser.stream)
            var_name = parser.stream.expect("name").value
            if parser.stream.current.test("name:silent"):
                next(parser.stream)
                silent = True

        body = parser.parse_statements(["name:endcapture"], drop_needle=True)

        if var_name and silent:
            # Assign captured content to variable, output nothing
            target = jinja2.nodes.Name(var_name, "store", lineno=lineno)
            return jinja2.nodes.AssignBlock(target, None, body).set_lineno(lineno)
        if var_name:
            # Assign and output
            output_nodes = list(body)
            target = jinja2.nodes.Name(var_name, "store", lineno=lineno)
            assign = jinja2.nodes.AssignBlock(target, None, body).set_lineno(lineno)
            return [assign, *output_nodes]
        # Just output
        return body


# ---------------------------------------------------------------------------
# Globals
# ---------------------------------------------------------------------------


@jinja2.pass_context
def _url(context: Any, viewname: str, *args: object, silent: bool = False, **kwargs: object) -> str:
    """Wrap ``reverse()``, optionally catching ``NoReverseMatch``."""
    try:
        request = context.get("request") if context else None
        current_app = getattr(request, "current_app", None) if request else None
        return reverse(viewname, args=args, kwargs=kwargs, current_app=current_app)
    except NoReverseMatch:
        if silent:
            return ""
        raise


def _now(format_string: str) -> str:
    """Return the current datetime formatted with Django's dateformat."""
    return dateformat(datetime.now(tz=timezone.get_current_timezone()), format_string)


# ---------------------------------------------------------------------------
# Unfold templatetag globals (from unfold.py)
# ---------------------------------------------------------------------------


@jinja2.pass_context
def _tab_list_jinja2(context: Any, page: str, opts: Any = None) -> Markup:
    from django_admin_boost.unfold.templatetags.unfold import tab_list

    result = tab_list(_jinja2_context_to_request_context(context), page, opts)
    return Markup(result)  # noqa: S704


@jinja2.pass_context
def _action_list_jinja2(context: Any) -> Markup:
    from django_admin_boost.unfold.templatetags.unfold import action_list

    result = action_list(_jinja2_context_to_request_context(context))
    return Markup(result)  # noqa: S704


@jinja2.pass_context
def _render_section_jinja2(context: Any, section_class: Any, instance: Any) -> Markup:
    from django_admin_boost.unfold.templatetags.unfold import render_section

    result = render_section(_jinja2_context_to_request_context(context), section_class, instance)
    return Markup(result)  # noqa: S704


def _has_nav_item_active(items: list) -> bool:
    for item in items:
        if item.get("active"):
            return True
    return False


@jinja2.pass_context
def _element_classes_jinja2(context: Any, key: str) -> str:
    element_classes = context.get("element_classes") or {}
    if key in element_classes:
        val = element_classes[key]
        if isinstance(val, (list, tuple)):
            return " ".join(val)
        return val
    return ""


@jinja2.pass_context
def _fieldset_rows_classes_jinja2(context: Any) -> str:
    from django_admin_boost.unfold.templatetags.unfold import fieldset_rows_classes

    return fieldset_rows_classes(_jinja2_context_to_request_context(context))


@jinja2.pass_context
def _fieldset_row_classes_jinja2(context: Any) -> str:
    from django_admin_boost.unfold.templatetags.unfold import fieldset_row_classes

    return fieldset_row_classes(_jinja2_context_to_request_context(context))


@jinja2.pass_context
def _fieldset_line_classes_jinja2(context: Any) -> str:
    from django_admin_boost.unfold.templatetags.unfold import fieldset_line_classes

    return fieldset_line_classes(_jinja2_context_to_request_context(context))


@jinja2.pass_context
def _action_item_classes_jinja2(context: Any, action: dict) -> str:
    from django_admin_boost.unfold.templatetags.unfold import action_item_classes

    return action_item_classes(_jinja2_context_to_request_context(context), action)


def _infinite_paginator_url(cl: Any, i: Any) -> str:
    from django_admin_boost.unfold.templatetags.unfold import infinite_paginator_url

    return infinite_paginator_url(cl, i)


def _elided_page_range(paginator: Any, number: int) -> Any:
    from django_admin_boost.unfold.templatetags.unfold import elided_page_range

    return elided_page_range(paginator, number)


@jinja2.pass_context
def _querystring_params_jinja2(context: Any, query_key: str, query_value: str) -> str:
    from django_admin_boost.unfold.templatetags.unfold import querystring_params

    return querystring_params(_jinja2_context_to_request_context(context), query_key, query_value)


@jinja2.pass_context
def _unfold_querystring_jinja2(context: Any, *args: Any, **kwargs: Any) -> str:
    from django_admin_boost.unfold.templatetags.unfold import unfold_querystring

    return unfold_querystring(_jinja2_context_to_request_context(context), *args, **kwargs)


@jinja2.pass_context
def _header_title_jinja2(context: Any) -> Markup:
    from django_admin_boost.unfold.templatetags.unfold import header_title

    result = header_title(_jinja2_context_to_request_context(context))
    return Markup(result)  # noqa: S704


@jinja2.pass_context
def _admin_object_app_url_jinja2(context: Any, obj: Any, arg: str) -> str:
    from django_admin_boost.unfold.templatetags.unfold import admin_object_app_url

    return admin_object_app_url(_jinja2_context_to_request_context(context), obj, arg)


def _tabs_primary_active(inlines: list) -> str:
    from django_admin_boost.unfold.templatetags.unfold import tabs_primary_active

    return tabs_primary_active(inlines)


@jinja2.pass_context
def _preserve_filters_jinja2(context: Any) -> Markup:
    from django_admin_boost.unfold.templatetags.unfold import preserve_changelist_filters

    result = preserve_changelist_filters(_jinja2_context_to_request_context(context))
    from django.template.loader import render_to_string

    return Markup(  # noqa: S704
        render_to_string(
            "unfold/templatetags/preserve_changelist_filters.html",
            context=result,
        ),
    )


# ---------------------------------------------------------------------------
# Unfold list templatetag globals (from unfold_list.py)
# ---------------------------------------------------------------------------


@jinja2.pass_context
def _unfold_result_list_jinja2(context: Any, cl: Any) -> Markup:
    from django_admin_boost.unfold.templatetags.unfold_list import result_list

    ctx = _jinja2_context_to_dict(context)
    result = result_list(ctx, cl)
    from django.template.loader import render_to_string

    return Markup(render_to_string("admin/change_list_results.html", context=result))  # noqa: S704


@jinja2.pass_context
def _unfold_search_form_jinja2(context: Any, cl: Any) -> Markup:
    from django_admin_boost.unfold.templatetags.unfold_list import unfold_search_form

    result = unfold_search_form(cl)
    from django.template.loader import render_to_string

    return Markup(render_to_string("admin/search_form.html", context=result))  # noqa: S704


@jinja2.pass_context
def _unfold_admin_actions_jinja2(context: Any, cl: Any) -> Markup:
    from django.contrib.admin.templatetags.admin_list import admin_actions

    ctx = _jinja2_context_to_dict(context)
    result = admin_actions(ctx)
    from django.template.loader import render_to_string

    return Markup(render_to_string("admin/dataset_actions.html", context=result))  # noqa: S704


def _result_headers(cl: Any) -> Any:
    from django_admin_boost.unfold.templatetags.unfold_list import result_headers

    return result_headers(cl)


def _results(cl: Any) -> Any:
    from django_admin_boost.unfold.templatetags.unfold_list import results

    return results(cl)


def _result_hidden_fields(cl: Any) -> Any:
    from django.contrib.admin.templatetags.admin_list import result_hidden_fields

    return result_hidden_fields(cl)


def _paginator_number(cl: Any, i: Any) -> Markup:
    from django_admin_boost.unfold.templatetags.unfold_list import paginator_number

    return Markup(paginator_number(cl, i))  # noqa: S704


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------


def _yesno(value: object, arg: str = "yes,no,maybe") -> str:
    bits = arg.split(",")
    if len(bits) < 2:  # noqa: PLR2004
        return str(value)
    yes, no = bits[0], bits[1]
    maybe = bits[2] if len(bits) > 2 else bits[1]  # noqa: PLR2004
    if value is None:
        return maybe
    if value:
        return yes
    return no


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


def _escapejs(value: str) -> str:
    from django.utils.html import escapejs

    return escapejs(value)


def _linebreaksbr(value: str) -> Markup:
    from django.utils.html import linebreaks

    return Markup(linebreaks(value))  # noqa: S704


def _slugify_filter(value: str) -> str:
    return slugify(value)


def _pluralize(value: Any, arg: str = "s") -> str:
    bits = arg.split(",")
    singular = bits[0] if len(bits) > 1 else ""
    plural = bits[-1]
    try:
        if int(value) != 1:
            return plural
    except (ValueError, TypeError):
        pass
    return singular


# ---------------------------------------------------------------------------
# Unfold-specific filters
# ---------------------------------------------------------------------------


def _has_active_item(items: list) -> bool:
    for item in items:
        if item.get("active"):
            return True
    return False


def _class_name(value: Any) -> str:
    return value.__class__.__name__


def _is_list(value: Any) -> bool:
    return isinstance(value, list)


def _index(indexable: Any, i: int) -> Any:
    try:
        return indexable[i]
    except (KeyError, TypeError, IndexError):
        return None


def _tabs(adminform: Any) -> list:
    from django_admin_boost.unfold.templatetags.unfold import tabs

    return tabs(adminform)


def _changeform_data(adminform: Any) -> Markup:
    from django_admin_boost.unfold.templatetags.unfold import changeform_data

    return Markup(changeform_data(adminform))  # noqa: S704


def _changeform_condition(field: Any) -> Any:
    from django_admin_boost.unfold.templatetags.unfold import changeform_condition

    return changeform_condition(field)


def _has_nested_tables(table: dict) -> bool:
    return any(isinstance(row, dict) and "table" in row for row in table.get("rows", []))


def _inline_add_button_text(json_string: str) -> str:
    return json.loads(json_string)["options"]["addText"]


def _add_css_class(field: Any, classes: Any) -> Any:
    from django_admin_boost.unfold.templatetags.unfold import add_css_class

    return add_css_class(field, classes)


def _tabs_active(fieldsets: list) -> str:
    from django_admin_boost.unfold.templatetags.unfold import tabs_active

    return tabs_active(fieldsets)


def _tabs_errors_count(fieldset: Any) -> int:
    from django_admin_boost.unfold.templatetags.unfold import tabs_errors_count

    return tabs_errors_count(fieldset)


def _unicoded_slugify(value: str) -> str:
    return slugify(value, allow_unicode=True)


# ---------------------------------------------------------------------------
# Context conversion helpers
# ---------------------------------------------------------------------------


def _jinja2_context_to_dict(context: Any) -> dict[str, Any]:
    """Convert a Jinja2 Context (immutable) to a plain dict."""
    if isinstance(context, dict):
        return context
    return dict(context)


def _jinja2_context_to_request_context(context: Any) -> Any:
    """Convert a Jinja2 Context to a Django RequestContext-like dict.

    Many unfold templatetags expect a RequestContext with .get() and ['request'].
    We create a simple wrapper that satisfies this interface.
    """
    ctx = _jinja2_context_to_dict(context)
    return _RequestContextProxy(ctx)


class _RequestContextProxy:
    """Minimal proxy that looks like a Django RequestContext to templatetags."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data
        self.request = data.get("request")

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __iter__(self):
        return iter(self._data)

    def flatten(self) -> dict[str, Any]:
        return dict(self._data)
