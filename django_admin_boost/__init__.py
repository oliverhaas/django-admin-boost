"""django-admin-boost: Performance-oriented Django admin extensions.

Standalone mixins and paginators that work with stock django.contrib.admin.
For the full Jinja2-compatible admin replacement, use ``django_admin_boost.admin``.

Importing this package installs an import hook that redirects
``django.contrib.admin`` to ``django_admin_boost.admin``.
"""

from django_admin_boost._redirect import install as _install_redirect
from django_admin_boost.mixins import ListFieldsMixin, SmartPaginatorMixin
from django_admin_boost.paginators import EstimatedCountPaginator

_install_redirect()

__all__ = [
    "EstimatedCountPaginator",
    "ListFieldsMixin",
    "SmartPaginatorMixin",
]
