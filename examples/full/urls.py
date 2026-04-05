from django_admin_boost.admin import site
from django.urls import path

urlpatterns = [
    path("admin/", site.urls),
]
