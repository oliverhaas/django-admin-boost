from django.urls import path

from django_admin_boost.admin import site

urlpatterns = [
    path("admin/", site.urls),
]
