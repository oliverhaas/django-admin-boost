from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from django_admin_boost.admin.options import ModelAdmin
from django_admin_boost.boost import site as boost_site
from tests.testapp.models import Article, Category

# Register models with the boost admin site for testing
if not boost_site.is_registered(Article):

    class _ArticleAdmin(ModelAdmin):
        list_display = ["title", "category", "status", "is_featured", "priority", "publish_date", "created_at"]
        list_display_links = ["title"]
        list_filter = ["status", "is_featured", "category"]
        search_fields = ["title", "slug", "body"]
        date_hierarchy = "created_at"
        readonly_fields = ["created_at"]
        fieldsets = [
            (None, {"fields": ["title", "slug", "body", "category"]}),
            ("Publishing", {"fields": ["status", "is_featured", "priority", "publish_date"]}),
            ("Metadata", {"fields": ["created_at"], "classes": ["collapse"]}),
        ]

    class _CategoryAdmin(ModelAdmin):
        list_display = ["name"]
        search_fields = ["name"]

    boost_site.register(Article, _ArticleAdmin)
    boost_site.register(Category, _CategoryAdmin)

BOOST_SETTINGS = {
    "ROOT_URLCONF": "tests.settings.boost_urls",
    "TEMPLATES": [
        {
            "BACKEND": "django.template.backends.jinja2.Jinja2",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "environment": "django_admin_boost.boost.jinja2_env.environment",
                "context_processors": [
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ],
}


@override_settings(**BOOST_SETTINGS)
class BoostAdminViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser("admin", "admin@test.com", "password")
        cls.category = Category.objects.create(name="Tech")
        cls.article = Article.objects.create(
            title="Test Article",
            slug="test-article",
            body="Test body",
            category=cls.category,
            status=Article.Status.PUBLISHED,
        )

    def setUp(self):
        self.client.force_login(self.admin_user)

    def test_index(self):
        response = self.client.get("/admin/")
        assert response.status_code == 200

    def test_app_index(self):
        response = self.client.get("/admin/testapp/")
        assert response.status_code == 200

    def test_change_list(self):
        response = self.client.get("/admin/testapp/article/")
        assert response.status_code == 200

    def test_add_form(self):
        response = self.client.get("/admin/testapp/article/add/")
        assert response.status_code == 200

    def test_change_form(self):
        response = self.client.get(f"/admin/testapp/article/{self.article.pk}/change/")
        assert response.status_code == 200

    def test_delete_confirmation(self):
        response = self.client.get(f"/admin/testapp/article/{self.article.pk}/delete/")
        assert response.status_code == 200

    def test_object_history(self):
        response = self.client.get(f"/admin/testapp/article/{self.article.pk}/history/")
        assert response.status_code == 200

    def test_login_page(self):
        self.client.logout()
        response = self.client.get("/admin/login/")
        assert response.status_code == 200


@override_settings(**BOOST_SETTINGS)
class BoostAdminSearchFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser("admin", "admin@test.com", "password")
        for i in range(25):
            Article.objects.create(
                title=f"Article {i}",
                status=Article.Status.PUBLISHED if i % 2 else Article.Status.DRAFT,
            )

    def setUp(self):
        self.client.force_login(self.admin_user)

    def test_search(self):
        response = self.client.get("/admin/testapp/article/?q=Article+1")
        assert response.status_code == 200

    def test_filter(self):
        response = self.client.get("/admin/testapp/article/?status__exact=published")
        assert response.status_code == 200
