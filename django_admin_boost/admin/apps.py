import importlib
import sys
import types
from pathlib import Path

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

# ---------------------------------------------------------------------------
# Make ``django.contrib.admin`` resolve to ``django_admin_boost.admin``.
#
# Most of our submodules can be imported before the app registry is ready,
# so we wire them into sys.modules directly at import time.  Two submodules
# (``forms`` and ``models``) import Django models at module level, which
# requires the app registry — those get lightweight stubs now and are
# replaced with the real modules in ``ready()``.
# ---------------------------------------------------------------------------

# Submodules that are safe to import before the app registry is ready.
_EAGER_SUBMODULES = [
    "actions",
    "checks",
    "decorators",
    "exceptions",
    "filters",
    "helpers",
    "options",
    "sites",
    "utils",
    "widgets",
]

# Submodules that import Django models at module level and need the app
# registry — they get empty stubs now, replaced in ready().
_DEFERRED_SUBMODULES = [
    "forms",
    "models",
]

_SUBPACKAGES = {
    "templatetags": ["admin_list", "admin_modify", "admin_urls", "base", "log"],
    "views": ["autocomplete", "decorators", "main"],
}


def _install_redirects() -> None:
    """Point ``django.contrib.admin`` at ``django_admin_boost.admin``.

    Called at import time.  Eagerly wires the top-level package and all
    submodules that can be imported before the app registry is ready.
    Installs lightweight stubs for ``forms``, ``models``, and subpackages
    that are replaced in ``SimpleAdminConfig.ready()``.
    """
    # Top-level: wire directly to our real module
    our_admin = importlib.import_module("django_admin_boost.admin")
    sys.modules["django.contrib.admin"] = our_admin

    # Eager submodules: import and wire directly
    for name in _EAGER_SUBMODULES:
        key = f"django.contrib.admin.{name}"
        if key not in sys.modules:
            mod = importlib.import_module(f"django_admin_boost.admin.{name}")
            sys.modules[key] = mod

    # Deferred submodules: lightweight stubs until ready()
    for name in _DEFERRED_SUBMODULES:
        key = f"django.contrib.admin.{name}"
        if key not in sys.modules:
            stub = types.ModuleType(key)
            stub.__package__ = "django.contrib.admin"
            sys.modules[key] = stub

    # Subpackages: lightweight stubs until ready()
    for pkg_name, children in _SUBPACKAGES.items():
        pkg_key = f"django.contrib.admin.{pkg_name}"
        if pkg_key not in sys.modules:
            pkg = types.ModuleType(pkg_key)
            pkg.__package__ = pkg_key
            pkg.__path__ = []
            sys.modules[pkg_key] = pkg
        for child in children:
            child_key = f"{pkg_key}.{child}"
            if child_key not in sys.modules:
                stub = types.ModuleType(child_key)
                stub.__package__ = pkg_key
                sys.modules[child_key] = stub


_install_redirects()


class SimpleAdminConfig(AppConfig):
    """Simple AppConfig which does not do automatic discovery."""

    default_auto_field = "django.db.models.AutoField"
    default_site = "django_admin_boost.admin.sites.AdminSite"
    label = "admin"
    name = "django_admin_boost.admin"
    verbose_name = _("Administration")

    def ready(self) -> None:
        from django.core import checks  # noqa: PLC0415

        from django_admin_boost.admin.checks import check_admin_app, check_dependencies  # noqa: PLC0415

        checks.register(check_dependencies, checks.Tags.admin)
        checks.register(check_admin_app, checks.Tags.admin)
        self._wire_deferred_modules()
        self._update_parent_attribute()
        self._monkeypatch_generics()
        self._ensure_admin_locale()

    def _wire_deferred_modules(self) -> None:
        """Replace stubs for forms, models, and subpackages with real modules."""
        for name in _DEFERRED_SUBMODULES:
            mod = importlib.import_module(f"django_admin_boost.admin.{name}")
            sys.modules[f"django.contrib.admin.{name}"] = mod

        for pkg_name, children in _SUBPACKAGES.items():
            pkg = importlib.import_module(f"django_admin_boost.admin.{pkg_name}")
            sys.modules[f"django.contrib.admin.{pkg_name}"] = pkg
            for child in children:
                mod = importlib.import_module(f"django_admin_boost.admin.{pkg_name}.{child}")
                sys.modules[f"django.contrib.admin.{pkg_name}.{child}"] = mod

    def _update_parent_attribute(self) -> None:
        """Update ``django.contrib.admin`` attribute on the parent package.

        Python checks the parent's attribute before ``sys.modules``, so
        ``from django.contrib import admin`` needs this to work.
        """
        import django.contrib  # noqa: PLC0415

        import django_admin_boost.admin as our_admin  # noqa: PLC0415

        django.contrib.admin = our_admin

    def _monkeypatch_generics(self) -> None:
        """Make our admin classes subscriptable for type-checking tools.

        Third-party packages like ``django-modeltranslation`` use
        ``BaseModelAdmin[_ModelT]`` at class definition time.  Since our
        classes are copies (not the originals that ``django-stubs-ext``
        patches), we pass them via ``extra_classes``.
        """
        import django_stubs_ext  # noqa: PLC0415

        from django_admin_boost.admin.options import BaseModelAdmin, ModelAdmin  # noqa: PLC0415

        django_stubs_ext.monkeypatch(extra_classes=[BaseModelAdmin, ModelAdmin])

    def _ensure_admin_locale(self) -> None:
        """Ensure Django's admin translation catalogue is still discoverable.

        Since this app replaces ``django.contrib.admin`` in the app registry,
        Django's ``all_locale_paths()`` no longer finds the original admin
        locale directory.  We add it to ``LOCALE_PATHS`` so translations for
        admin-specific strings (e.g. "Save and continue editing") still work.
        """
        import django  # noqa: PLC0415
        from django.conf import settings  # noqa: PLC0415

        admin_locale = Path(django.__file__).parent / "contrib" / "admin" / "locale"
        if admin_locale.is_dir():
            admin_locale_str = str(admin_locale)
            locale_paths = list(getattr(settings, "LOCALE_PATHS", []))
            if admin_locale_str not in locale_paths:
                settings.LOCALE_PATHS = [*locale_paths, admin_locale_str]


class AdminConfig(SimpleAdminConfig):
    """The default AppConfig for admin which does autodiscovery."""

    default = True

    def ready(self) -> None:
        super().ready()
        self.module.autodiscover()  # type: ignore[union-attr]
