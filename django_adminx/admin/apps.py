import types

from django.apps import AppConfig
from django.core import checks
from django.utils.translation import gettext_lazy as _

from django_adminx.admin.checks import check_admin_app, check_dependencies


def _make_django_admin_importable() -> None:
    """Ensure ``import django.contrib.admin.models`` doesn't crash.

    When ``django.contrib.admin`` is not in INSTALLED_APPS, importing its
    ``models`` module triggers a RuntimeError because Django's LogEntry
    model class can't resolve its app_label.

    We insert a placeholder module into ``sys.modules`` so that
    ``from django.contrib.admin.models import LogEntry`` resolves without
    actually loading the original module. Once our app is ready, the
    ``ready()`` method replaces this placeholder with our real models.
    """
    import sys  # noqa: PLC0415

    key = "django.contrib.admin.models"
    if key not in sys.modules:
        # Create a placeholder module that will be replaced in ready()
        placeholder = types.ModuleType(key)
        placeholder.__package__ = "django.contrib.admin"
        sys.modules[key] = placeholder


_make_django_admin_importable()


class SimpleAdminConfig(AppConfig):
    """Simple AppConfig which does not do automatic discovery."""

    default_auto_field = "django.db.models.AutoField"
    default_site = "django_adminx.admin.sites.AdminSite"
    label = "admin"
    name = "django_adminx.admin"
    verbose_name = _("Administration")

    def ready(self) -> None:
        checks.register(check_dependencies, checks.Tags.admin)
        checks.register(check_admin_app, checks.Tags.admin)
        self._patch_django_admin()

    def _patch_django_admin(self) -> None:
        """Redirect ``django.contrib.admin`` references to our implementation.

        Third-party apps (including ``django.contrib.auth``) import from
        ``django.contrib.admin`` and register models on its ``site`` singleton.
        Without these patches, those registrations land on Django's site instead
        of ours, and ``isinstance`` checks in Django's ``@register`` decorator
        fail because our ``AdminSite`` is a separate class.

        These patches are unavoidable because:

        1. **Site singleton (patches 1-2):** Django's ``@admin.register()``
           decorator lazy-imports ``from django.contrib.admin.sites import site``
           at call time. We must redirect this reference so third-party model
           registrations land on our site.

        2. **AdminSite class (patches 3-4):** The same decorator does
           ``isinstance(admin_site, AdminSite)`` using Django's class. Since our
           AdminSite is a standalone copy (not a subclass), this check fails
           without the patch.

        3. **Models module (patch 5):** Replace the placeholder
           ``django.contrib.admin.models`` with our real models so that
           ``from django.contrib.admin.models import LogEntry`` works.
        """
        import sys  # noqa: PLC0415

        import django.contrib.admin as django_admin  # noqa: PLC0415
        import django.contrib.admin.sites as django_admin_sites  # noqa: PLC0415

        from django_adminx.admin import models as our_models  # noqa: PLC0415
        from django_adminx.admin.sites import AdminSite, site  # noqa: PLC0415

        django_admin.site = site  # type: ignore[assignment]
        django_admin_sites.site = site  # type: ignore[assignment]
        django_admin_sites.AdminSite = AdminSite  # type: ignore[misc,assignment]
        django_admin.AdminSite = AdminSite  # type: ignore[misc,assignment]

        # Replace placeholder with our real models module
        sys.modules["django.contrib.admin.models"] = our_models
        django_admin.models = our_models


class AdminConfig(SimpleAdminConfig):
    """The default AppConfig for admin which does autodiscovery."""

    default = True

    def ready(self) -> None:
        super().ready()
        self.module.autodiscover()  # type: ignore[union-attr]
