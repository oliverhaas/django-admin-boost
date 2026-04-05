"""Tests for the ListFieldsMixin (list_only_fields, list_defer_fields, auto mode)."""

from __future__ import annotations

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory, TestCase
from django.urls import resolve

from django_adminx import admin
from django_adminx.admin import ModelAdmin
from django_adminx.mixins import ListFieldsMixin
from tests.testapp.models import Article


class _ChangelistTestBase(TestCase):
    """Shared helpers for changelist mixin tests."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.superuser = User.objects.create_superuser(username="admin", password="password")

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.site = admin.AdminSite()

    def _changelist_request(self):
        request = self.factory.get("/admin/testapp/article/")
        request.user = self.superuser
        request.resolver_match = resolve("/admin/testapp/article/")
        return request

    def _change_request(self, pk=1):
        request = self.factory.get(f"/admin/testapp/article/{pk}/change/")
        request.user = self.superuser
        request.resolver_match = resolve(f"/admin/testapp/article/{pk}/change/")
        return request


class TestListOnlyFields(_ChangelistTestBase):
    """list_only_fields applies .only() with pk always included."""

    def test_only_applied_on_changelist(self) -> None:
        class Admin(ModelAdmin):
            list_only_fields = ["title", "status"]

        ma = Admin(Article, self.site)
        qs = ma.get_queryset(self._changelist_request())
        deferred_fields, is_defer = qs.query.deferred_loading
        assert is_defer is False
        assert "id" in deferred_fields, "pk must always be included"
        assert set(deferred_fields) == {"id", "title", "status"}

    def test_pk_auto_included(self) -> None:
        """Even if the user doesn't list pk, it's included."""

        class Admin(ModelAdmin):
            list_only_fields = ["title"]

        ma = Admin(Article, self.site)
        qs = ma.get_queryset(self._changelist_request())
        deferred_fields, is_defer = qs.query.deferred_loading
        assert is_defer is False
        assert "id" in deferred_fields

    def test_empty_list_means_pk_only(self) -> None:
        """list_only_fields = [] means .only(pk)."""

        class Admin(ModelAdmin):
            list_only_fields = []

        ma = Admin(Article, self.site)
        qs = ma.get_queryset(self._changelist_request())
        deferred_fields, is_defer = qs.query.deferred_loading
        assert is_defer is False
        assert set(deferred_fields) == {"id"}

    def test_not_applied_on_change_view(self) -> None:
        class Admin(ModelAdmin):
            list_only_fields = ["title"]

        article = Article.objects.create(title="Test")
        ma = Admin(Article, self.site)
        qs = ma.get_queryset(self._change_request(article.pk))
        deferred_fields, is_defer = qs.query.deferred_loading
        assert is_defer is True
        assert len(deferred_fields) == 0


class TestListDeferFields(_ChangelistTestBase):
    """list_defer_fields applies .defer()."""

    def test_defer_applied_on_changelist(self) -> None:
        class Admin(ModelAdmin):
            list_defer_fields = ["body", "slug"]

        ma = Admin(Article, self.site)
        qs = ma.get_queryset(self._changelist_request())
        deferred_fields, is_defer = qs.query.deferred_loading
        assert is_defer is True
        assert set(deferred_fields) == {"body", "slug"}

    def test_empty_list_means_no_optimization(self) -> None:
        """list_defer_fields = [] is the opt-out escape hatch."""

        class Admin(ModelAdmin):
            list_defer_fields = []

        ma = Admin(Article, self.site)
        qs = ma.get_queryset(self._changelist_request())
        deferred_fields, is_defer = qs.query.deferred_loading
        assert is_defer is True
        assert len(deferred_fields) == 0

    def test_not_applied_on_change_view(self) -> None:
        class Admin(ModelAdmin):
            list_defer_fields = ["body"]

        article = Article.objects.create(title="Test")
        ma = Admin(Article, self.site)
        qs = ma.get_queryset(self._change_request(article.pk))
        deferred_fields, is_defer = qs.query.deferred_loading
        assert is_defer is True
        assert len(deferred_fields) == 0


class TestMutualExclusivity(_ChangelistTestBase):
    """Setting both list_only_fields and list_defer_fields raises an error."""

    def test_both_set_raises_error(self) -> None:
        class Admin(ModelAdmin):
            list_only_fields = ["title"]
            list_defer_fields = ["body"]

        ma = Admin(Article, self.site)
        with pytest.raises(ImproperlyConfigured, match="Cannot set both"):
            ma.get_queryset(self._changelist_request())

    def test_both_set_empty_raises_error(self) -> None:
        """Even two empty lists conflict — the user must pick one."""

        class Admin(ModelAdmin):
            list_only_fields = []
            list_defer_fields = []

        ma = Admin(Article, self.site)
        with pytest.raises(ImproperlyConfigured, match="Cannot set both"):
            ma.get_queryset(self._changelist_request())


class TestAutoMode(_ChangelistTestBase):
    """When neither attribute is set, auto mode resolves list_display to fields."""

    def test_auto_resolves_list_display_fields(self) -> None:
        class Admin(ModelAdmin):
            list_display = ["title", "status", "created_at"]

        ma = Admin(Article, self.site)
        qs = ma.get_queryset(self._changelist_request())
        deferred_fields, is_defer = qs.query.deferred_loading
        assert is_defer is False
        assert "id" in deferred_fields
        assert set(deferred_fields) == {"id", "title", "status", "created_at"}

    def test_auto_includes_pk(self) -> None:
        class Admin(ModelAdmin):
            list_display = ["title"]

        ma = Admin(Article, self.site)
        qs = ma.get_queryset(self._changelist_request())
        deferred_fields, is_defer = qs.query.deferred_loading
        assert is_defer is False
        assert "id" in deferred_fields

    def test_auto_str_maps_to_pk(self) -> None:
        """__str__ in list_display contributes only pk."""

        class Admin(ModelAdmin):
            list_display = ["__str__"]

        ma = Admin(Article, self.site)
        qs = ma.get_queryset(self._changelist_request())
        deferred_fields, is_defer = qs.query.deferred_loading
        assert is_defer is False
        assert set(deferred_fields) == {"id"}

    def test_auto_skips_callables(self) -> None:
        """Callables/methods that aren't concrete fields are ignored."""

        class Admin(ModelAdmin):
            list_display = ["title", "upper_title"]

            def upper_title(self, obj):
                return obj.title.upper()

        ma = Admin(Article, self.site)
        qs = ma.get_queryset(self._changelist_request())
        deferred_fields, is_defer = qs.query.deferred_loading
        assert is_defer is False
        # upper_title is a method, not a field — only title and pk
        assert set(deferred_fields) == {"id", "title"}

    def test_auto_not_applied_on_change_view(self) -> None:
        class Admin(ModelAdmin):
            list_display = ["title"]

        article = Article.objects.create(title="Test")
        ma = Admin(Article, self.site)
        qs = ma.get_queryset(self._change_request(article.pk))
        deferred_fields, is_defer = qs.query.deferred_loading
        assert is_defer is True
        assert len(deferred_fields) == 0

    def test_auto_handles_fk_field(self) -> None:
        """A ForeignKey in list_display should include the _id column."""

        class Admin(ModelAdmin):
            list_display = ["title", "category"]

        ma = Admin(Article, self.site)
        qs = ma.get_queryset(self._changelist_request())
        deferred_fields, is_defer = qs.query.deferred_loading
        assert is_defer is False
        assert "category_id" in deferred_fields or "category" in deferred_fields


class TestListFieldsMixinExport(_ChangelistTestBase):
    """ListFieldsMixin is importable from the expected locations."""

    def test_importable_from_mixins(self) -> None:

        assert ListFieldsMixin is not None

    def test_importable_from_top_level(self) -> None:
        from django_adminx import ListFieldsMixin

        assert ListFieldsMixin is not None

    def test_importable_from_admin(self) -> None:
        from django_adminx.admin import ListFieldsMixin

        assert ListFieldsMixin is not None
