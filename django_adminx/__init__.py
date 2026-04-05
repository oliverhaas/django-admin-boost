"""django-adminx: Performance-oriented Django admin extensions.

Standalone mixins and paginators that work with stock django.contrib.admin.
For the full Jinja2-compatible admin replacement, use ``django_adminx.admin``.
"""

from django_adminx.mixins import ListFieldsMixin, SmartPaginatorMixin
from django_adminx.paginators import EstimatedCountPaginator

__all__ = [
    "EstimatedCountPaginator",
    "ListFieldsMixin",
    "SmartPaginatorMixin",
]
