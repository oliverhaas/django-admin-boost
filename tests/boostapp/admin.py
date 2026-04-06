from django_admin_boost.boost import ModelAdmin, register
from tests.testapp.models import Article, Category


@register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@register(Article)
class ArticleAdmin(ModelAdmin):
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
