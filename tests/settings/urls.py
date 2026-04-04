from django.urls import path

from django_adminx.admin import site

urlpatterns = [
    path("admin/", site.urls),
]
