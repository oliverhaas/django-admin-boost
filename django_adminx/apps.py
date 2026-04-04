from django.apps import AppConfig
from django.core import checks
from django.utils.translation import gettext_lazy as _

from django_adminx.checks import check_admin_app, check_dependencies


class SimpleAdminConfig(AppConfig):
    """Simple AppConfig which does not do automatic discovery."""

    default_auto_field = "django.db.models.AutoField"
    default_site = "django_adminx.sites.AdminSite"
    label = "admin"
    name = "django_adminx"
    verbose_name = _("Administration")

    def ready(self) -> None:
        checks.register(check_dependencies, checks.Tags.admin)
        checks.register(check_admin_app, checks.Tags.admin)
        self._patch_django_admin()

    def _patch_django_admin(self) -> None:
        """Make django.contrib.admin.site point to our site singleton.

        Third-party apps (including django.contrib.auth) import from
        django.contrib.admin and register models on its ``site`` object.
        We redirect that singleton so registrations land on our AdminSite.
        """
        import django.contrib.admin as django_admin  # noqa: PLC0415
        import django.contrib.admin.sites as django_admin_sites  # noqa: PLC0415

        from django_adminx.sites import AdminSite, site  # noqa: PLC0415

        # Redirect Django's admin site singleton to ours
        django_admin.site = site
        django_admin_sites.site = site

        # Make isinstance checks pass for our AdminSite
        django_admin_sites.AdminSite = AdminSite
        django_admin.AdminSite = AdminSite


class AdminConfig(SimpleAdminConfig):
    """The default AppConfig for admin which does autodiscovery."""

    default = True

    def ready(self) -> None:
        super().ready()
        self.module.autodiscover()
