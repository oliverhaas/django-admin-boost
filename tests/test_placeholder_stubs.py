import sys

import django_admin_boost.admin


def test_top_level_is_our_module():
    """django.contrib.admin should point directly at our module."""
    mod = sys.modules.get("django.contrib.admin")
    assert mod is django_admin_boost.admin


def test_admin_site_importable():
    """AdminSite and ModelAdmin should be importable from django.contrib.admin."""
    mod = sys.modules["django.contrib.admin"]
    assert hasattr(mod, "AdminSite")
    assert hasattr(mod, "ModelAdmin")


def test_eager_submodule_is_real_module():
    """Eager submodules (sites, options) should be our real modules, not stubs."""
    import django_admin_boost.admin.sites

    mod = sys.modules.get("django.contrib.admin.sites")
    assert mod is django_admin_boost.admin.sites
    assert hasattr(mod, "AdminSite")


def test_deferred_submodule_has_attrs_after_ready():
    """Deferred submodules (forms, models) should have attrs after ready()."""
    mod = sys.modules.get("django.contrib.admin.forms")
    assert mod is not None
    assert hasattr(mod, "AdminAuthenticationForm")


def test_options_has_model_admin():
    import django_admin_boost.admin.options

    mod = sys.modules.get("django.contrib.admin.options")
    assert mod is django_admin_boost.admin.options
    assert hasattr(mod, "ModelAdmin")
