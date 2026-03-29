from django.contrib import admin

from django_adminx import BaseModelAdmin

from .models import Article


@admin.register(Article)
class ArticleAdmin(BaseModelAdmin):
    list_display = ["title", "status", "created_at"]
    list_only_fields = ["id", "title", "status", "created_at"]
