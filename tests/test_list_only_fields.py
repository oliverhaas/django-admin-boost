"""Tests for the list_only_fields feature."""

from __future__ import annotations

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import resolve

from django_adminx import BaseModelAdmin, ListOnlyFieldsMixin
from tests.testapp.models import Article


class ListOnlyFieldsChangelistTest(TestCase):
    """Test that .only() is applied on changelist views."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.superuser = User.objects.create_superuser(username="admin", password="password")

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.site = admin.AdminSite()

        class TestArticleAdmin(BaseModelAdmin):
            list_display = ["title", "status", "created_at"]
            list_only_fields = ["id", "title", "status", "created_at"]

        self.model_admin = TestArticleAdmin(Article, self.site)

    def _make_changelist_request(self) -> object:
        """Create a request that looks like a changelist request."""
        request = self.factory.get("/admin/testapp/article/")
        request.user = self.superuser
        # Resolve so resolver_match is set
        request.resolver_match = resolve("/admin/testapp/article/")
        return request

    def test_only_applied_on_changelist(self) -> None:
        request = self._make_changelist_request()
        qs = self.model_admin.get_queryset(request)
        # Django sets query.deferred_loading when .only() is used
        deferred_fields, is_defer = qs.query.deferred_loading
        # .only() sets is_defer=False (immediate loading) with the listed fields
        assert is_defer is False, "Expected .only() to be applied (deferred_loading mode)"
        assert set(deferred_fields) == {"id", "title", "status", "created_at"}

    def test_queryset_still_works(self) -> None:
        """Ensure the queryset actually executes without errors."""
        Article.objects.create(title="Hello", status="published")
        request = self._make_changelist_request()
        qs = self.model_admin.get_queryset(request)
        assert qs.count() == 1
        article = qs.first()
        assert article is not None
        assert article.title == "Hello"


class ListOnlyFieldsChangeViewTest(TestCase):
    """Test that .only() is NOT applied on change views."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.superuser = User.objects.create_superuser(username="admin", password="password")

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.site = admin.AdminSite()

        class TestArticleAdmin(BaseModelAdmin):
            list_only_fields = ["id", "title"]

        self.model_admin = TestArticleAdmin(Article, self.site)

    def test_only_not_applied_on_change_view(self) -> None:
        article = Article.objects.create(title="Test")
        request = self.factory.get(f"/admin/testapp/article/{article.pk}/change/")
        request.user = self.superuser
        request.resolver_match = resolve(f"/admin/testapp/article/{article.pk}/change/")
        qs = self.model_admin.get_queryset(request)
        deferred_fields, is_defer = qs.query.deferred_loading
        # No .only() means deferred_loading is (frozenset(), True) by default
        assert is_defer is True
        assert len(deferred_fields) == 0

    def test_only_not_applied_on_add_view(self) -> None:
        request = self.factory.get("/admin/testapp/article/add/")
        request.user = self.superuser
        request.resolver_match = resolve("/admin/testapp/article/add/")
        qs = self.model_admin.get_queryset(request)
        deferred_fields, is_defer = qs.query.deferred_loading
        assert is_defer is True
        assert len(deferred_fields) == 0


class ListOnlyFieldsNotSetTest(TestCase):
    """Test that when list_only_fields is not set, get_queryset is a no-op."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.superuser = User.objects.create_superuser(username="admin", password="password")

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.site = admin.AdminSite()

        class PlainArticleAdmin(BaseModelAdmin):
            pass  # no list_only_fields

        self.model_admin = PlainArticleAdmin(Article, self.site)

    def test_no_only_when_attribute_not_set(self) -> None:
        request = self.factory.get("/admin/testapp/article/")
        request.user = self.superuser
        request.resolver_match = resolve("/admin/testapp/article/")
        qs = self.model_admin.get_queryset(request)
        deferred_fields, is_defer = qs.query.deferred_loading
        # Default queryset — no .only() applied
        assert is_defer is True
        assert len(deferred_fields) == 0

    def test_no_only_when_attribute_is_none(self) -> None:
        self.model_admin.list_only_fields = None
        request = self.factory.get("/admin/testapp/article/")
        request.user = self.superuser
        request.resolver_match = resolve("/admin/testapp/article/")
        qs = self.model_admin.get_queryset(request)
        deferred_fields, is_defer = qs.query.deferred_loading
        assert is_defer is True

    def test_no_only_when_attribute_is_empty(self) -> None:
        self.model_admin.list_only_fields = []
        request = self.factory.get("/admin/testapp/article/")
        request.user = self.superuser
        request.resolver_match = resolve("/admin/testapp/article/")
        qs = self.model_admin.get_queryset(request)
        deferred_fields, is_defer = qs.query.deferred_loading
        assert is_defer is True


class ListOnlyFieldsMixinStandaloneTest(TestCase):
    """Test using the mixin directly with a custom ModelAdmin."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.superuser = User.objects.create_superuser(username="admin", password="password")

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.site = admin.AdminSite()

        class CustomAdmin(ListOnlyFieldsMixin, ModelAdmin):
            list_only_fields = ["id", "title", "status"]

        self.model_admin = CustomAdmin(Article, self.site)

    def test_mixin_works_with_plain_modeladmin(self) -> None:
        request = self.factory.get("/admin/testapp/article/")
        request.user = self.superuser
        request.resolver_match = resolve("/admin/testapp/article/")
        qs = self.model_admin.get_queryset(request)
        deferred_fields, is_defer = qs.query.deferred_loading
        assert is_defer is False
        assert set(deferred_fields) == {"id", "title", "status"}
