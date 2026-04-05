"""Tests for list_only_fields (explicit whitelist mode of ListFieldsMixin)."""

from __future__ import annotations

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import resolve

from django_admin_boost import admin
from django_admin_boost.admin import ModelAdmin
from tests.testapp.models import Article


class ListOnlyFieldsChangelistTest(TestCase):
    """Test that .only() is applied on changelist views."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.superuser = User.objects.create_superuser(username="admin", password="password")

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.site = admin.AdminSite()

        class TestArticleAdmin(ModelAdmin):
            list_display = ["title", "status", "created_at"]
            list_only_fields = ["id", "title", "status", "created_at"]

        self.model_admin = TestArticleAdmin(Article, self.site)

    def _make_changelist_request(self) -> object:
        """Create a request that looks like a changelist request."""
        request = self.factory.get("/admin/testapp/article/")
        request.user = self.superuser
        request.resolver_match = resolve("/admin/testapp/article/")
        return request

    def test_only_applied_on_changelist(self) -> None:
        request = self._make_changelist_request()
        qs = self.model_admin.get_queryset(request)
        deferred_fields, is_defer = qs.query.deferred_loading
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

        class TestArticleAdmin(ModelAdmin):
            list_only_fields = ["id", "title"]

        self.model_admin = TestArticleAdmin(Article, self.site)

    def test_only_not_applied_on_change_view(self) -> None:
        article = Article.objects.create(title="Test")
        request = self.factory.get(f"/admin/testapp/article/{article.pk}/change/")
        request.user = self.superuser
        request.resolver_match = resolve(f"/admin/testapp/article/{article.pk}/change/")
        qs = self.model_admin.get_queryset(request)
        deferred_fields, is_defer = qs.query.deferred_loading
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


class ListOnlyFieldsOptOutTest(TestCase):
    """Test that list_defer_fields=[] opts out of all optimization."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.superuser = User.objects.create_superuser(username="admin", password="password")

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.site = admin.AdminSite()

    def test_defer_empty_disables_optimization(self) -> None:
        class PlainArticleAdmin(ModelAdmin):
            list_defer_fields = []  # opt-out

        model_admin = PlainArticleAdmin(Article, self.site)
        request = self.factory.get("/admin/testapp/article/")
        request.user = self.superuser
        request.resolver_match = resolve("/admin/testapp/article/")
        qs = model_admin.get_queryset(request)
        deferred_fields, is_defer = qs.query.deferred_loading
        assert is_defer is True
        assert len(deferred_fields) == 0

    def test_only_empty_means_pk_only(self) -> None:
        class PkOnlyAdmin(ModelAdmin):
            list_only_fields = []

        model_admin = PkOnlyAdmin(Article, self.site)
        request = self.factory.get("/admin/testapp/article/")
        request.user = self.superuser
        request.resolver_match = resolve("/admin/testapp/article/")
        qs = model_admin.get_queryset(request)
        deferred_fields, is_defer = qs.query.deferred_loading
        assert is_defer is False
        assert set(deferred_fields) == {"id"}


class ListFieldsMixinStandaloneTest(TestCase):
    """Test using the mixin directly with a custom ModelAdmin."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.superuser = User.objects.create_superuser(username="admin", password="password")

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.site = admin.AdminSite()

        class CustomAdmin(ModelAdmin):
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
