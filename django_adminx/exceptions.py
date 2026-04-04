from django.core.exceptions import SuspiciousOperation


class DisallowedModelAdminLookup(SuspiciousOperation):
    """Invalid filter was passed to admin view via URL querystring"""


class DisallowedModelAdminToField(SuspiciousOperation):
    """Invalid to_field was passed to admin view via URL query string"""


class AlreadyRegistered(Exception):
    """The model is already registered."""


class NotRegistered(Exception):
    """The model is not registered."""
