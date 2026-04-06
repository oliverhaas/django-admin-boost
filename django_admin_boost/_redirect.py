"""Import hook that redirects ``django.contrib.admin`` to ``django_admin_boost.admin``.

Install by importing ``django_admin_boost`` before Django loads::

    # manage.py, wsgi.py, or asgi.py — at the very top
    import django_admin_boost

After this, every ``import django.contrib.admin`` or
``from django.contrib.admin import ModelAdmin`` anywhere in the process
transparently returns the django-admin-boost version.
"""

from __future__ import annotations

import importlib
import sys
from importlib.abc import MetaPathFinder
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import ModuleType

_PREFIX = "django.contrib.admin"
_TARGET = "django_admin_boost.admin"

# These submodules define Django models — their __module__ must match an
# INSTALLED_APPS entry for the app registry to find them.  We let them
# import normally.
_SKIP = frozenset(
    {
        f"{_PREFIX}.forms",
        f"{_PREFIX}.models",
    },
)


class _AdminRedirectFinder(MetaPathFinder):
    """Intercept imports of ``django.contrib.admin`` and redirect them."""

    def find_module(
        self,
        fullname: str,
        path: object = None,  # noqa: ARG002
    ) -> _AdminRedirectFinder | None:
        if fullname in _SKIP:
            return None
        if fullname == _PREFIX or fullname.startswith(f"{_PREFIX}."):
            return self
        return None

    def load_module(self, fullname: str) -> ModuleType:
        if fullname in sys.modules:
            return sys.modules[fullname]

        # django.contrib.admin.sites → django_admin_boost.admin.sites
        our_name = _TARGET + fullname[len(_PREFIX) :]
        mod = importlib.import_module(our_name)
        sys.modules[fullname] = mod
        return mod


def install() -> None:
    """Install the import hook if not already installed."""
    if any(isinstance(f, _AdminRedirectFinder) for f in sys.meta_path):
        return

    sys.meta_path.insert(0, _AdminRedirectFinder())

    # Eagerly wire the top-level module so `from django.contrib import admin`
    # resolves to ours. Python checks parent-package attributes before
    # sys.modules for `from X import Y` syntax.
    import django.contrib  # noqa: PLC0415

    our_admin = importlib.import_module(_TARGET)
    sys.modules[_PREFIX] = our_admin
    django.contrib.admin = our_admin  # type: ignore[attr-defined]
