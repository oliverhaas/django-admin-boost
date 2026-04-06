from django.apps import AppConfig


class BoostAdminConfig(AppConfig):
    name = "django_admin_boost.boost"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        self.module.autodiscover()  # type: ignore[union-attr]
