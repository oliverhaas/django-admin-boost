from django.apps import AppConfig
from django.contrib import admin
from django.contrib.admin import sites

from django_admin_boost.unfold.sites import UnfoldAdminSite


class DefaultAppConfig(AppConfig):
    name = "django_admin_boost.unfold"
    default = True

    def ready(self) -> None:
        site = UnfoldAdminSite()

        admin.site = site
        sites.site = site


class BasicAppConfig(AppConfig):
    name = "django_admin_boost.unfold"
