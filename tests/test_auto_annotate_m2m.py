"""Tests for auto-annotation of M2M fields in list_display with Count()."""

import pytest
from django.contrib.admin import site as admin_site
from django.test import RequestFactory
from django.urls import resolve

from django_admin_boost.admin import ModelAdmin
from tests.testapp.models import Article, Tag


@pytest.fixture
def superuser(db):
    from django.contrib.auth.models import User

    return User.objects.create_superuser(username="admin", password="password")


@pytest.fixture
def rf():
    return RequestFactory()


@pytest.fixture
def tagged_article(db):
    tag1 = Tag.objects.create(name="python")
    tag2 = Tag.objects.create(name="django")
    article = Article.objects.create(title="Test Article")
    article.tags.add(tag1, tag2)
    return article


def test_m2m_field_auto_annotated(rf, superuser, tagged_article):
    class TestAdmin(ModelAdmin):
        list_display = ["title", "tags"]

    ma = TestAdmin(Article, admin_site)
    request = rf.get("/admin/testapp/article/")
    request.user = superuser
    request.resolver_match = resolve("/admin/testapp/article/")
    qs = ma.get_queryset(request)
    assert "tags_count" in qs.query.annotations


def test_m2m_count_value_correct(rf, superuser, tagged_article):
    class TestAdmin(ModelAdmin):
        list_display = ["title", "tags"]

    ma = TestAdmin(Article, admin_site)
    request = rf.get("/admin/testapp/article/")
    request.user = superuser
    request.resolver_match = resolve("/admin/testapp/article/")
    qs = ma.get_queryset(request)
    article = qs.get(pk=tagged_article.pk)
    assert article.tags_count == 2


def test_m2m_skipped_when_custom_callable_exists(rf, superuser, db):
    class TestAdmin(ModelAdmin):
        list_display = ["title", "tags"]

        def tags(self, obj):
            return "custom"

    ma = TestAdmin(Article, admin_site)
    request = rf.get("/admin/testapp/article/")
    request.user = superuser
    request.resolver_match = resolve("/admin/testapp/article/")
    qs = ma.get_queryset(request)
    assert "tags_count" not in qs.query.annotations


def test_m2m_get_list_display_replaces_field_with_callable(rf, superuser, db):
    class TestAdmin(ModelAdmin):
        list_display = ["title", "tags"]

    ma = TestAdmin(Article, admin_site)
    request = rf.get("/admin/testapp/article/")
    request.user = superuser
    request.resolver_match = resolve("/admin/testapp/article/")
    list_display = ma.get_list_display(request)
    # "tags" should have been replaced by a callable
    assert "tags" not in list_display
    callables = [f for f in list_display if callable(f)]
    assert len(callables) == 1
    count_fn = callables[0]
    assert count_fn.short_description == "Tags"
    assert count_fn.admin_order_field == "tags_count"


def test_m2m_callable_returns_count(rf, superuser, tagged_article):
    class TestAdmin(ModelAdmin):
        list_display = ["title", "tags"]

    ma = TestAdmin(Article, admin_site)
    request = rf.get("/admin/testapp/article/")
    request.user = superuser
    request.resolver_match = resolve("/admin/testapp/article/")
    qs = ma.get_queryset(request)
    article = qs.get(pk=tagged_article.pk)

    list_display = ma.get_list_display(request)
    count_fn = next(f for f in list_display if callable(f))
    assert count_fn(article) == 2
