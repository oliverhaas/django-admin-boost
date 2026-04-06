"""Tests for the EstimatedCountPaginator and SmartPaginatorMixin."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import User

from django_admin_boost import EstimatedCountPaginator
from django_admin_boost.admin import ModelAdmin
from tests.testapp.models import Article


@pytest.fixture
def articles_25(db):
    return [Article.objects.create(title=f"Article {i}", status="published") for i in range(25)]


@pytest.fixture
def articles_10(db):
    return [Article.objects.create(title=f"Article {i}", status="published") for i in range(10)]


@pytest.fixture
def articles_mixed(db):
    published = [Article.objects.create(title=f"Article {i}", status="published") for i in range(10)]
    drafts = [Article.objects.create(title=f"Draft {i}", status="draft") for i in range(5)]
    return published, drafts


@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(username="admin", password="password")


def _mock_pg_connection(mock_connections, reltuples):
    """Set up mock_connections to simulate a PostgreSQL backend with given reltuples."""
    mock_conn = MagicMock()
    mock_conn.vendor = "postgresql"
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = reltuples
    mock_cursor.__enter__ = lambda self: self
    mock_cursor.__exit__ = MagicMock(return_value=False)
    mock_conn.cursor.return_value = mock_cursor
    mock_connections.__getitem__.return_value = mock_conn
    return mock_conn


# --- SQLite fallback ---


def test_count_returns_real_count_on_sqlite(articles_25):
    paginator = EstimatedCountPaginator(Article.objects.all(), per_page=10)
    assert paginator.count == 25


def test_num_pages_correct(articles_25):
    paginator = EstimatedCountPaginator(Article.objects.all(), per_page=10)
    assert paginator.num_pages == 3


def test_page_returns_correct_objects(articles_25):
    paginator = EstimatedCountPaginator(Article.objects.order_by("id"), per_page=10)
    assert len(paginator.page(1).object_list) == 10
    assert len(paginator.page(3).object_list) == 5


def test_empty_queryset(db):
    paginator = EstimatedCountPaginator(Article.objects.none(), per_page=10)
    assert paginator.count == 0
    assert paginator.num_pages == 1


# --- Filtered fallback ---


def test_filtered_queryset_uses_real_count(articles_mixed):
    paginator = EstimatedCountPaginator(Article.objects.filter(status="published"), per_page=10)
    assert paginator.count == 10


def test_filtered_queryset_pages(articles_mixed):
    paginator = EstimatedCountPaginator(Article.objects.filter(status="draft"), per_page=3)
    assert paginator.num_pages == 2


# --- PostgreSQL estimation path (mocked) ---


@patch("django_admin_boost.paginators.connections")
def test_unfiltered_uses_estimate_on_postgres(mock_connections, articles_10):
    _mock_pg_connection(mock_connections, (50000.0,))
    paginator = EstimatedCountPaginator(Article.objects.all(), per_page=10)
    assert paginator.count == 50000


@patch("django_admin_boost.paginators.connections")
def test_zero_estimate_falls_back_to_real_count(mock_connections, articles_10):
    """When reltuples is 0 (never analysed), use real COUNT."""
    _mock_pg_connection(mock_connections, (0.0,))
    paginator = EstimatedCountPaginator(Article.objects.all(), per_page=10)
    assert paginator.count == 10


@patch("django_admin_boost.paginators.connections")
def test_negative_estimate_falls_back_to_real_count(mock_connections, articles_10):
    """When reltuples is -1 (table never analysed), use real COUNT."""
    _mock_pg_connection(mock_connections, (-1.0,))
    paginator = EstimatedCountPaginator(Article.objects.all(), per_page=10)
    assert paginator.count == 10


@patch("django_admin_boost.paginators.connections")
def test_filtered_queryset_skips_estimate_even_on_postgres(mock_connections, articles_10):
    """Filtered querysets should never use the estimate."""
    mock_conn = MagicMock()
    mock_conn.vendor = "postgresql"
    mock_connections.__getitem__.return_value = mock_conn

    paginator = EstimatedCountPaginator(Article.objects.filter(status="published"), per_page=10)
    assert paginator.count == 10
    mock_conn.cursor.assert_not_called()


@patch("django_admin_boost.paginators.connections")
def test_no_row_in_pg_class_falls_back(mock_connections, articles_10):
    """When pg_class has no matching row, fall back to real COUNT."""
    _mock_pg_connection(mock_connections, None)
    paginator = EstimatedCountPaginator(Article.objects.all(), per_page=10)
    assert paginator.count == 10


# --- Non-QuerySet ---


def test_list_object_list_uses_len():
    paginator = EstimatedCountPaginator(list(range(42)), per_page=10)
    assert paginator.count == 42
    assert paginator.num_pages == 5


# --- is_approximate_count ---


def test_not_approximate_on_sqlite(articles_10):
    paginator = EstimatedCountPaginator(Article.objects.all(), per_page=10)
    assert paginator.is_approximate_count is False


def test_not_approximate_for_plain_list():
    paginator = EstimatedCountPaginator(list(range(42)), per_page=10)
    assert paginator.is_approximate_count is False


def test_not_approximate_for_filtered_queryset(articles_10):
    paginator = EstimatedCountPaginator(Article.objects.filter(status="published"), per_page=10)
    assert paginator.is_approximate_count is False


@patch("django_admin_boost.paginators.connections")
def test_approximate_when_estimate_used(mock_connections, articles_10):
    _mock_pg_connection(mock_connections, (50000.0,))
    paginator = EstimatedCountPaginator(Article.objects.all(), per_page=10)
    assert paginator.is_approximate_count is True
    assert paginator.count == 50000


@patch("django_admin_boost.paginators.connections")
def test_not_approximate_when_estimate_zero(mock_connections, articles_10):
    _mock_pg_connection(mock_connections, (0.0,))
    paginator = EstimatedCountPaginator(Article.objects.all(), per_page=10)
    assert paginator.is_approximate_count is False


# --- SmartPaginatorMixin ---


def test_model_admin_has_estimated_paginator():
    assert ModelAdmin.paginator is EstimatedCountPaginator


def test_model_admin_has_show_full_result_count_false():
    assert ModelAdmin.show_full_result_count is False


# --- Admin integration ---


def test_changelist_view_uses_estimated_paginator(client, superuser, articles_25):
    client.force_login(superuser)
    response = client.get("/admin/testapp/article/")
    assert response.status_code == 200
    cl = response.context["cl"]
    assert isinstance(cl.paginator, EstimatedCountPaginator)
    assert cl.paginator.count == 25


def test_changelist_pagination_works(client, superuser, articles_25):
    client.force_login(superuser)
    response = client.get("/admin/testapp/article/?p=1")
    assert response.status_code == 200
