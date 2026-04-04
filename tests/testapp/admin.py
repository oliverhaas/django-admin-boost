import django_adminx as admin

from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "created_at"]
    list_only_fields = ["id", "title", "status", "created_at"]
