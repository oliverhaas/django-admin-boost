import sys


def test_admin_site_importable_from_placeholder():
    """AdminSite should be importable from django.contrib.admin before ready()."""
    mod = sys.modules.get("django.contrib.admin")
    assert mod is not None
    assert hasattr(mod, "AdminSite")
    assert hasattr(mod, "ModelAdmin")


def test_submodule_sites_has_admin_site():
    mod = sys.modules.get("django.contrib.admin.sites")
    assert mod is not None
    assert hasattr(mod, "AdminSite")


def test_submodule_forms_has_auth_form():
    mod = sys.modules.get("django.contrib.admin.forms")
    assert mod is not None
    assert hasattr(mod, "AdminAuthenticationForm")


def test_submodule_options_has_model_admin():
    mod = sys.modules.get("django.contrib.admin.options")
    assert mod is not None
    assert hasattr(mod, "ModelAdmin")
