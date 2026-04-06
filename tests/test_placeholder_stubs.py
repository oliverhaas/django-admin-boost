"""Tests for the django.contrib.admin → django_admin_boost.admin import redirect."""

import sys

import django_admin_boost.admin


def test_hook_is_installed():
    from django_admin_boost._redirect import _AdminRedirectFinder

    assert any(isinstance(f, _AdminRedirectFinder) for f in sys.meta_path)


def test_top_level_is_our_module():
    """django.contrib.admin should be our module."""
    mod = sys.modules.get("django.contrib.admin")
    assert mod is django_admin_boost.admin


def test_import_admin_site():
    from django.contrib.admin import AdminSite

    from django_admin_boost.admin.sites import AdminSite as OurAdminSite

    assert AdminSite is OurAdminSite


def test_import_model_admin():
    from django.contrib.admin import ModelAdmin

    from django_admin_boost.admin.options import ModelAdmin as OurModelAdmin

    assert ModelAdmin is OurModelAdmin


def test_submodule_import():
    from django.contrib.admin import sites

    import django_admin_boost.admin.sites

    assert sites is django_admin_boost.admin.sites


def test_deep_submodule_import():
    from django.contrib.admin.views import main

    import django_admin_boost.admin.views.main

    assert main is django_admin_boost.admin.views.main


def test_forms_not_redirected():
    """forms imports auth models — must NOT be redirected by the hook."""
    from django_admin_boost._redirect import _SKIP

    assert "django.contrib.admin.forms" in _SKIP


def test_models_not_redirected():
    """models defines LogEntry — must NOT be redirected by the hook."""
    from django_admin_boost._redirect import _SKIP

    assert "django.contrib.admin.models" in _SKIP
