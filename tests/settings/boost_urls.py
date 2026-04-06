from django.urls import path

from django_admin_boost.boost import site

urlpatterns = [
    path("admin/", site.urls),
]
