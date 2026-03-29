"""
Performance-oriented Django admin extensions.
"""

from django_adminx.admin import BaseModelAdmin
from django_adminx.mixins import ListOnlyFieldsMixin, SmartPaginatorMixin
from django_adminx.paginators import EstimatedCountPaginator

__all__ = [
    "BaseModelAdmin",
    "EstimatedCountPaginator",
    "ListOnlyFieldsMixin",
    "SmartPaginatorMixin",
]
