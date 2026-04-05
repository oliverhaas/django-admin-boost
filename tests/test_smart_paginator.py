"""Tests for the EstimatedCountPaginator and SmartPaginatorMixin."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase

from django_admin_boost import EstimatedCountPaginator
from django_admin_boost.admin import ModelAdmin
from tests.testapp.models import Article


class EstimatedCountPaginatorSQLiteFallbackTest(TestCase):
    """On non-PostgreSQL backends the paginator must fall back to real COUNT."""

    @classmethod
    def setUpTestData(cls) -> None:
        for i in range(25):
            Article.objects.create(title=f"Article {i}", status="published")

    def test_count_returns_real_count_on_sqlite(self) -> None:
        qs = Article.objects.all()
        paginator = EstimatedCountPaginator(qs, per_page=10)
        assert paginator.count == 25

    def test_num_pages_correct(self) -> None:
        qs = Article.objects.all()
        paginator = EstimatedCountPaginator(qs, per_page=10)
        assert paginator.num_pages == 3

    def test_page_returns_correct_objects(self) -> None:
        qs = Article.objects.order_by("id")
        paginator = EstimatedCountPaginator(qs, per_page=10)
        page = paginator.page(1)
        assert len(page.object_list) == 10
        page3 = paginator.page(3)
        assert len(page3.object_list) == 5

    def test_empty_queryset(self) -> None:
        qs = Article.objects.none()
        paginator = EstimatedCountPaginator(qs, per_page=10)
        assert paginator.count == 0
        assert paginator.num_pages == 1


class EstimatedCountPaginatorFilteredFallbackTest(TestCase):
    """When the queryset is filtered, fall back to real COUNT even on PostgreSQL."""

    @classmethod
    def setUpTestData(cls) -> None:
        for i in range(10):
            Article.objects.create(title=f"Article {i}", status="published")
        for i in range(5):
            Article.objects.create(title=f"Draft {i}", status="draft")

    def test_filtered_queryset_uses_real_count(self) -> None:
        qs = Article.objects.filter(status="published")
        paginator = EstimatedCountPaginator(qs, per_page=10)
        assert paginator.count == 10

    def test_filtered_queryset_pages(self) -> None:
        qs = Article.objects.filter(status="draft")
        paginator = EstimatedCountPaginator(qs, per_page=3)
        assert paginator.num_pages == 2


class EstimatedCountPaginatorPostgresPathTest(TestCase):
    """Test the PostgreSQL estimation path using mocks."""

    @classmethod
    def setUpTestData(cls) -> None:
        for i in range(10):
            Article.objects.create(title=f"Article {i}", status="published")

    @patch("django_admin_boost.paginators.connections")
    def test_unfiltered_uses_estimate_on_postgres(self, mock_connections: MagicMock) -> None:
        mock_conn = MagicMock()
        mock_conn.vendor = "postgresql"
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (50000.0,)
        mock_cursor.__enter__ = lambda self: self
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_connections.__getitem__.return_value = mock_conn

        qs = Article.objects.all()
        paginator = EstimatedCountPaginator(qs, per_page=10)
        assert paginator.count == 50000

    @patch("django_admin_boost.paginators.connections")
    def test_zero_estimate_falls_back_to_real_count(self, mock_connections: MagicMock) -> None:
        """When reltuples is 0 (never analysed), use real COUNT."""
        mock_conn = MagicMock()
        mock_conn.vendor = "postgresql"
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (0.0,)
        mock_cursor.__enter__ = lambda self: self
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_connections.__getitem__.return_value = mock_conn

        qs = Article.objects.all()
        paginator = EstimatedCountPaginator(qs, per_page=10)
        # Should fall back — the real count is 10
        assert paginator.count == 10

    @patch("django_admin_boost.paginators.connections")
    def test_negative_estimate_falls_back_to_real_count(self, mock_connections: MagicMock) -> None:
        """When reltuples is -1 (table never analysed), use real COUNT."""
        mock_conn = MagicMock()
        mock_conn.vendor = "postgresql"
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (-1.0,)
        mock_cursor.__enter__ = lambda self: self
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_connections.__getitem__.return_value = mock_conn

        qs = Article.objects.all()
        paginator = EstimatedCountPaginator(qs, per_page=10)
        assert paginator.count == 10

    @patch("django_admin_boost.paginators.connections")
    def test_filtered_queryset_skips_estimate_even_on_postgres(self, mock_connections: MagicMock) -> None:
        """Filtered querysets should never use the estimate."""
        mock_conn = MagicMock()
        mock_conn.vendor = "postgresql"
        mock_connections.__getitem__.return_value = mock_conn

        qs = Article.objects.filter(status="published")
        paginator = EstimatedCountPaginator(qs, per_page=10)
        assert paginator.count == 10
        # The cursor should never have been opened for the estimate
        mock_conn.cursor.assert_not_called()

    @patch("django_admin_boost.paginators.connections")
    def test_no_row_in_pg_class_falls_back(self, mock_connections: MagicMock) -> None:
        """When pg_class has no matching row, fall back to real COUNT."""
        mock_conn = MagicMock()
        mock_conn.vendor = "postgresql"
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_cursor.__enter__ = lambda self: self
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_connections.__getitem__.return_value = mock_conn

        qs = Article.objects.all()
        paginator = EstimatedCountPaginator(qs, per_page=10)
        assert paginator.count == 10


class EstimatedCountPaginatorNonQuerysetTest(TestCase):
    """Test with a plain list instead of a QuerySet."""

    def test_list_object_list_uses_len(self) -> None:
        paginator = EstimatedCountPaginator(list(range(42)), per_page=10)
        assert paginator.count == 42
        assert paginator.num_pages == 5


class SmartPaginatorMixinTest(TestCase):
    """Test that SmartPaginatorMixin sets the right class attributes."""

    def test_model_admin_has_estimated_paginator(self) -> None:
        assert ModelAdmin.paginator is EstimatedCountPaginator

    def test_model_admin_has_show_full_result_count_false(self) -> None:
        assert ModelAdmin.show_full_result_count is False


class SmartPaginatorAdminIntegrationTest(TestCase):
    """Test that the paginator integrates correctly with the admin changelist."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.superuser = User.objects.create_superuser(username="admin", password="password")
        for i in range(25):
            Article.objects.create(title=f"Article {i}", status="published")

    def test_changelist_view_uses_estimated_paginator(self) -> None:
        self.client.force_login(self.superuser)
        response = self.client.get("/admin/testapp/article/")
        assert response.status_code == 200
        cl = response.context["cl"]
        assert isinstance(cl.paginator, EstimatedCountPaginator)
        assert cl.paginator.count == 25

    def test_changelist_pagination_works(self) -> None:
        self.client.force_login(self.superuser)
        response = self.client.get("/admin/testapp/article/?p=1")
        assert response.status_code == 200
