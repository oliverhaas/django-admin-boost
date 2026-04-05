"""Tests for the Jinja2 environment factory."""

from datetime import UTC

import pytest
from django.test import RequestFactory, override_settings

from django_adminx.admin.jinja2_env import (
    _admin_urlname,
    _admin_urlquote,
    _date_filter,
    _get_admin_log,
    _now,
    _yesno,
    environment,
)


class TestEnvironmentFactory:
    def test_creates_environment(self):
        env = environment(autoescape=True)
        assert env is not None
        assert "static" in env.globals
        assert "url" in env.globals
        assert "now" in env.globals
        assert "get_admin_log" in env.globals
        assert "get_current_language" in env.globals

    def test_has_filters(self):
        env = environment(autoescape=True)
        assert "capfirst" in env.filters
        assert "yesno" in env.filters
        assert "admin_urlname" in env.filters
        assert "admin_urlquote" in env.filters

    def test_i18n_extension_loaded(self):
        env = environment(autoescape=True)
        assert "jinja2.ext.InternationalizationExtension" in env.extensions


class TestUrlGlobal:
    def _render_url(self, template_str, context=None):
        """Render a Jinja2 template string using the admin environment."""
        env = environment(autoescape=True)
        template = env.from_string(template_str)
        return template.render(context or {})

    def test_resolves_admin_index(self):
        result = self._render_url('{{ url("admin:index") }}')
        assert result == "/admin/"

    def test_raises_on_missing_view(self):
        from django.urls import NoReverseMatch

        with pytest.raises(NoReverseMatch):
            self._render_url('{{ url("nonexistent-view-name") }}')

    def test_silent_returns_empty_on_missing_view(self):
        result = self._render_url('{{ url("nonexistent-view-name", silent=True) }}')
        assert result == ""

    def test_passes_current_app_from_request(self):
        """Issue #3: _url must pass current_app to reverse() for custom admin sites."""
        from unittest.mock import patch

        env = environment(autoescape=True)
        factory = RequestFactory()
        request = factory.get("/")
        request.current_app = "my_custom_admin"

        template = env.from_string('{{ url("admin:index") }}')
        with patch("django_adminx.admin.jinja2_env.reverse", return_value="/custom/") as mock_reverse:
            result = template.render({"request": request})

        mock_reverse.assert_called_once()
        call_kwargs = mock_reverse.call_args
        assert call_kwargs.kwargs.get("current_app") == "my_custom_admin", (
            f"Expected current_app='my_custom_admin' to be passed to reverse(), but got: {call_kwargs}"
        )


class TestNowGlobal:
    def test_returns_utc_offset(self):
        result = _now("Z")
        # UTC offset like "+0000" or "+00:00"
        assert isinstance(result, str)
        assert len(result) > 0

    @override_settings(TIME_ZONE="America/New_York", USE_TZ=True)
    def test_respects_server_timezone(self):
        """Issue #1: _now must use the server timezone, not hardcoded UTC."""
        from django.utils import timezone

        timezone.activate("America/New_York")
        try:
            result = _now("e")  # timezone name, e.g. "EST" or "EDT"
            # Should NOT be "UTC"
            assert result != "UTC", (
                "_now returned timezone 'UTC' but TIME_ZONE is 'America/New_York' — "
                "expected an Eastern timezone like 'EST' or 'EDT'"
            )
        finally:
            timezone.deactivate()


class TestYesnoFilter:
    def test_true_value(self):
        assert _yesno(True, "yes,no,maybe") == "yes"

    def test_false_value(self):
        assert _yesno(False, "yes,no,maybe") == "no"

    def test_none_value(self):
        assert _yesno(None, "yes,no,maybe") == "maybe"

    def test_none_without_maybe(self):
        assert _yesno(None, "yes,no") == "no"

    def test_default_arg(self):
        assert _yesno(True) == "yes"
        assert _yesno(False) == "no"


class TestAdminUrlnameFilter:
    def test_returns_url_name(self):

        class FakeOpts:
            app_label = "auth"
            model_name = "user"

        result = _admin_urlname(FakeOpts(), "changelist")
        assert result == "admin:auth_user_changelist"


class TestAdminUrlquoteFilter:
    def test_quotes_special_chars(self):
        assert _admin_urlquote("hello world") == "hello%20world"

    def test_preserves_safe_chars(self):
        assert _admin_urlquote("hello") == "hello"


class TestDateFilter:
    def test_none_returns_empty(self):
        assert _date_filter(None) == ""

    def test_empty_string_returns_empty(self):
        """Issue #6: _date_filter must handle empty strings like Django's date filter."""
        result = _date_filter("")
        assert result == "", f"Expected empty string for empty input, got AttributeError or '{result}'"

    def test_formats_datetime(self):
        from datetime import datetime

        dt = datetime(2024, 6, 15, 12, 0, 0, tzinfo=UTC)
        result = _date_filter(dt, "Y-m-d")
        assert result == "2024-06-15"


@pytest.mark.django_db
class TestGetAdminLog:
    def test_returns_empty_for_no_entries(self):
        result = _get_admin_log(10)
        assert list(result) == []

    def test_respects_limit(self):
        result = _get_admin_log(5)
        assert result.query.is_sliced
