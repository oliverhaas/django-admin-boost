from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SimpleAdminConfig(AppConfig):
    """Simple AppConfig which does not do automatic discovery."""

    default_auto_field = "django.db.models.AutoField"
    default_site = "django.contrib.admin.sites.AdminSite"
    label = "admin_boost"
    name = "django_admin_boost.admin"
    verbose_name = _("Administration")

    def ready(self) -> None:
        self._monkeypatch_generics()

    def _monkeypatch_generics(self) -> None:
        """Make our admin classes subscriptable for type-checking tools."""
        import django_stubs_ext  # noqa: PLC0415

        from django_admin_boost.admin import ModelAdmin  # noqa: PLC0415

        django_stubs_ext.monkeypatch(extra_classes=[ModelAdmin])


class AdminConfig(SimpleAdminConfig):
    """The default AppConfig for admin which does autodiscovery."""

    default = True

    def ready(self) -> None:
        super().ready()
        from django.contrib.admin import autodiscover  # noqa: PLC0415

        autodiscover()
