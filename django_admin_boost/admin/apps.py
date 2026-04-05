import importlib
import sys
import types
from pathlib import Path

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

# ---------------------------------------------------------------------------
# Make ``django.contrib.admin`` resolve to ``django_admin_boost.admin``.
#
# We insert placeholder modules into sys.modules at import time so that
# ``from django.contrib.admin.models import LogEntry`` (or any submodule)
# doesn't crash with RuntimeError before the app registry is ready.
#
# In ``ready()``, we replace all placeholders with our real modules.
# ---------------------------------------------------------------------------

_DJANGO_ADMIN_SUBMODULES = [
    "actions",
    "checks",
    "decorators",
    "exceptions",
    "filters",
    "forms",
    "helpers",
    "models",
    "options",
    "sites",
    "utils",
    "widgets",
]

_DJANGO_ADMIN_SUBPACKAGES = {
    "templatetags": ["admin_list", "admin_modify", "admin_urls", "base", "log"],
    "views": ["autocomplete", "decorators", "main"],
}


def _install_placeholders() -> None:
    """Pre-populate sys.modules with placeholders for django.contrib.admin.

    This prevents RuntimeError/ImportError when third-party code does
    ``from django.contrib.admin.models import LogEntry`` before the app
    registry is ready.  All placeholders are replaced with real modules
    in ``SimpleAdminConfig.ready()``.
    """
    # Top-level package placeholder
    if "django.contrib.admin" not in sys.modules:
        pkg = types.ModuleType("django.contrib.admin")
        pkg.__package__ = "django.contrib.admin"
        pkg.__path__ = []
        sys.modules["django.contrib.admin"] = pkg

    for name in _DJANGO_ADMIN_SUBMODULES:
        key = f"django.contrib.admin.{name}"
        if key not in sys.modules:
            mod = types.ModuleType(key)
            mod.__package__ = "django.contrib.admin"
            sys.modules[key] = mod

    for pkg_name, children in _DJANGO_ADMIN_SUBPACKAGES.items():
        pkg_key = f"django.contrib.admin.{pkg_name}"
        if pkg_key not in sys.modules:
            pkg = types.ModuleType(pkg_key)
            pkg.__package__ = pkg_key
            pkg.__path__ = []
            sys.modules[pkg_key] = pkg
        for child in children:
            child_key = f"{pkg_key}.{child}"
            if child_key not in sys.modules:
                mod = types.ModuleType(child_key)
                mod.__package__ = pkg_key
                sys.modules[child_key] = mod


_install_placeholders()


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
        self._redirect_django_admin()
        self._monkeypatch_generics()
        self._ensure_admin_locale()

    def _redirect_django_admin(self) -> None:
        """Replace all placeholders with our real modules.

        After this, ``from django.contrib.admin import ModelAdmin`` returns
        our ModelAdmin, ``from django.contrib.admin.models import LogEntry``
        returns our LogEntry, etc.
        """
        import django.contrib  # noqa: PLC0415

        import django_admin_boost.admin as our_admin  # noqa: PLC0415

        sys.modules["django.contrib.admin"] = our_admin
        # Also update the parent-package attribute so that
        # ``from django.contrib import admin`` returns our module
        # (Python checks the parent's attribute before sys.modules).
        django.contrib.admin = our_admin

        for name in _DJANGO_ADMIN_SUBMODULES:
            mod = importlib.import_module(f"django_admin_boost.admin.{name}")
            sys.modules[f"django.contrib.admin.{name}"] = mod

        for pkg_name, children in _DJANGO_ADMIN_SUBPACKAGES.items():
            pkg = importlib.import_module(f"django_admin_boost.admin.{pkg_name}")
            sys.modules[f"django.contrib.admin.{pkg_name}"] = pkg
            for child in children:
                mod = importlib.import_module(f"django_admin_boost.admin.{pkg_name}.{child}")
                sys.modules[f"django.contrib.admin.{pkg_name}.{child}"] = mod

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
