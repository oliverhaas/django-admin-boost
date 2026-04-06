from pathlib import Path

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


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
        self._monkeypatch_generics()
        self._ensure_admin_locale()

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
