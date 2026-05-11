"""Tests for the unmanaged admin kernel."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

import pytest
from django.contrib import admin as django_admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import AnonymousUser, User
from django.core.paginator import Paginator
from django.http import QueryDict
from django.test import RequestFactory

from django_admin_boost.unmanaged import (
    UnmanagedModel,
    UnmanagedModelAdmin,
    UnmanagedModelError,
    UnmanagedQuerySet,
)
from django_admin_boost.unmanaged.admin import _SinglePagePaginator
from django_admin_boost.unmanaged.querysets import _FakeQuery
from tests.unmanagedapp.admin import CacheAdmin, ListUnmanagedQuerySet
from tests.unmanagedapp.models import CacheEntry, Thing

if TYPE_CHECKING:
    from collections.abc import Iterator

    from django.db.models import Model


# --- UnmanagedModel ----------------------------------------------------------


def test_unmanaged_model_is_abstract():
    assert UnmanagedModel._meta.abstract is True


def test_meta_managed_is_false():
    assert Thing._meta.managed is False
    assert CacheEntry._meta.managed is False


def test_save_raises():
    thing = Thing(key="x", label="X")
    with pytest.raises(UnmanagedModelError, match="cannot be saved"):
        thing.save()


def test_delete_raises():
    thing = Thing(key="x", label="X")
    with pytest.raises(UnmanagedModelError, match="cannot be deleted"):
        thing.delete()


def test_unmanaged_model_error_is_database_error():
    from django.db.utils import DatabaseError, NotSupportedError

    assert issubclass(UnmanagedModelError, NotSupportedError)
    assert issubclass(UnmanagedModelError, DatabaseError)


def test_str_default_returns_pk():
    assert str(Thing(key="abc")) == "abc"


def test_str_default_handles_unset_pk():
    # CharField pk defaults to "" — the default __str__ just stringifies whatever pk is.
    assert str(Thing()) == ""


# --- UnmanagedModel.register -------------------------------------------------


@pytest.fixture
def fresh_site():
    return AdminSite(name="freshsite")


def test_register_attaches_admin_to_passed_site(fresh_site):
    class ThingAdmin(UnmanagedModelAdmin):
        pass

    Thing.register(ThingAdmin, site=fresh_site)
    assert Thing in fresh_site._registry
    assert isinstance(fresh_site._registry[Thing], ThingAdmin)


def test_register_uses_default_site_when_none():
    class ThingAdmin(UnmanagedModelAdmin):
        pass

    # The default site already has CacheEntry registered via autodiscover; pick Thing instead.
    assert Thing not in django_admin.site._registry
    try:
        Thing.register(ThingAdmin)
        assert Thing in django_admin.site._registry
        assert isinstance(django_admin.site._registry[Thing], ThingAdmin)
    finally:
        django_admin.site.unregister(Thing)


# --- UnmanagedQuerySet -------------------------------------------------------


class ToyQuerySet(UnmanagedQuerySet):
    def __init__(self, model: type[Model], items: list[Any]) -> None:
        super().__init__(model)
        self._items = items

    def count(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._items)

    def __getitem__(self, key: int | slice) -> Any:
        return self._items[key]

    def filter(self, *args: Any, pk__in: list[Any] | None = None, **kwargs: Any) -> Self:
        if pk__in is None:
            return self
        return type(self)(self.model, [x for x in self._items if x.pk in pk__in])

    def order_by(self, *fields: str) -> Self:
        return self


def _toy_qs(n: int = 10) -> ToyQuerySet:
    items = [Thing(key=str(i), label=f"item-{i}") for i in range(n)]
    return ToyQuerySet(Thing, items)


def test_queryset_protocol_with_paginator():
    qs = _toy_qs(13)
    paginator = Paginator(qs, per_page=5)
    assert paginator.count == 13
    assert paginator.num_pages == 3
    page1 = paginator.page(1).object_list
    assert len(page1) == 5
    page3 = paginator.page(3).object_list
    assert len(page3) == 3


def test_queryset_len():
    assert len(_toy_qs(7)) == 7


def test_queryset_bool_true():
    assert bool(_toy_qs(3)) is True


def test_queryset_bool_false():
    assert bool(_toy_qs(0)) is False


def test_queryset_iter():
    qs = _toy_qs(3)
    items = list(qs)
    assert [t.pk for t in items] == ["0", "1", "2"]


def test_queryset_noops_are_chainable():
    qs = _toy_qs(3)
    assert qs.select_related() is qs
    assert qs.distinct() is qs
    assert qs.alias() is qs
    assert qs.only() is qs
    assert qs.defer() is qs
    assert qs._clone() is qs
    assert qs._next_is_sticky() is qs
    assert qs.all() is qs


def test_queryset_query_attr_has_required_protocol():
    qs = _toy_qs(0)
    assert isinstance(qs.query, _FakeQuery)
    assert qs.query.select_related is False
    assert qs.query.order_by == ()
    assert qs.query.where == ()
    assert qs.query.model is Thing


def test_queryset_class_protocol_attrs():
    qs = _toy_qs(0)
    assert qs.ordered is True
    assert qs.db == "default"
    assert qs.model is Thing


def test_queryset_base_abstract_methods_raise():
    bare = UnmanagedQuerySet(Thing)
    with pytest.raises(NotImplementedError):
        bare.count()
    with pytest.raises(NotImplementedError):
        iter(bare)
    with pytest.raises(NotImplementedError):
        bare[0]
    with pytest.raises(NotImplementedError):
        bare.filter()
    with pytest.raises(NotImplementedError):
        bare.order_by()
    with pytest.raises(NotImplementedError):
        bare.none()


# --- UnmanagedModelAdmin ----------------------------------------------------


def _admin_for(model: type[UnmanagedModel] = Thing, **attrs: Any) -> UnmanagedModelAdmin:
    cls = type("_TestAdmin", (UnmanagedModelAdmin,), attrs)
    return cls(model, django_admin.site)


def test_default_permissions_are_false():
    a = _admin_for()
    request = RequestFactory().get("/")
    assert a.has_add_permission(request) is False
    assert a.has_change_permission(request) is False
    assert a.has_delete_permission(request) is False


def test_get_queryset_raises_by_default():
    a = _admin_for()
    request = RequestFactory().get("/")
    with pytest.raises(NotImplementedError):
        a.get_queryset(request)


def test_get_actions_strips_delete_selected():
    a = _admin_for(
        has_delete_permission=lambda self, request, obj=None: True,
    )
    request = RequestFactory().get("/")
    request.user = User(is_superuser=True, is_active=True, is_staff=True)
    actions = a.get_actions(request)
    assert "delete_selected" not in actions


def test_get_actions_handles_no_actions():
    a = _admin_for()
    request = RequestFactory().get("/")
    request.user = AnonymousUser()
    # Should not raise even though delete_selected isn't present.
    actions = a.get_actions(request)
    assert "delete_selected" not in actions


def test_get_paginator_default_when_pagination_enabled():
    a = _admin_for()
    paginator = a.get_paginator(RequestFactory().get("/"), _toy_qs(10), per_page=2)
    assert type(paginator) is Paginator
    assert paginator.num_pages == 5


def test_get_paginator_single_page_when_disabled():
    a = _admin_for(disable_list_pagination=True)
    paginator = a.get_paginator(RequestFactory().get("/"), _toy_qs(10), per_page=2)
    assert isinstance(paginator, _SinglePagePaginator)
    assert paginator.num_pages == 1


# --- extra_changelist_params -------------------------------------------------


def test_strip_extra_params_removes_keys_and_stashes_on_request():
    a = _admin_for(extra_changelist_params=("cursor", "help"))
    request = RequestFactory().get("/?cursor=abc&help=1&q=foo")
    a._strip_extra_params(request)
    assert "cursor" not in request.GET
    assert "help" not in request.GET
    assert request.GET["q"] == "foo"
    assert request._unmanaged_params == {"cursor": "abc", "help": "1"}


def test_strip_extra_params_keeps_other_params_intact():
    a = _admin_for(extra_changelist_params=("cursor",))
    request = RequestFactory().get("/?cursor=x&q=foo&page=2")
    a._strip_extra_params(request)
    assert request.GET["q"] == "foo"
    assert request.GET["page"] == "2"


def test_strip_extra_params_no_match_leaves_get_alone():
    a = _admin_for(extra_changelist_params=("cursor",))
    request = RequestFactory().get("/?q=foo")
    a._strip_extra_params(request)
    assert request.GET["q"] == "foo"
    assert request._unmanaged_params == {}


def test_request_get_immutable_before_strip_documents_the_trap():
    # The QueryDict on the request is non-mutable; the strip helper must use .copy().
    request = RequestFactory().get("/?cursor=abc")
    with pytest.raises(AttributeError):
        request.GET["new"] = "value"


def test_request_get_remains_usable_after_strip():
    a = _admin_for(extra_changelist_params=("cursor",))
    request = RequestFactory().get("/?cursor=abc&q=foo")
    a._strip_extra_params(request)
    # The mutable copy assigned back is still a QueryDict and still readable.
    assert isinstance(request.GET, QueryDict)
    assert list(request.GET.keys()) == ["q"]


# --- end-to-end smoke -------------------------------------------------------


@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(username="boss", password="password")


def test_changelist_view_smoke(client, superuser):
    client.force_login(superuser)
    response = client.get("/admin/unmanagedapp/cacheentry/")
    assert response.status_code == 200
    assert b"alpha" in response.content
    assert b"beta" in response.content


def test_extra_changelist_params_round_trip_via_http(client, superuser):
    client.force_login(superuser)
    response = client.get("/admin/unmanagedapp/cacheentry/?cursor=abc")
    assert response.status_code == 200
    assert CacheAdmin.captured_params == {"cursor": "abc"}


def test_extra_changelist_params_ignored_when_absent(client, superuser):
    client.force_login(superuser)
    response = client.get("/admin/unmanagedapp/cacheentry/")
    assert response.status_code == 200
    assert CacheAdmin.captured_params == {}


def test_smoke_uses_list_unmanaged_queryset(client, superuser):
    # Sanity: our toy queryset class is the one wired up; if someone swaps it,
    # this test catches the regression.
    client.force_login(superuser)
    response = client.get("/admin/unmanagedapp/cacheentry/")
    cl = response.context["cl"]
    assert isinstance(cl.queryset, ListUnmanagedQuerySet)
