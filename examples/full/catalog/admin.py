import django_adminx.admin as admin
from import_export.admin import ImportExportModelAdmin
from modeltranslation.admin import TranslationAdmin

from .models import Category, Product
from .resources import CategoryResource, ProductResource


@admin.register(Category)
class CategoryAdmin(TranslationAdmin, ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = CategoryResource
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(Product)
class ProductAdmin(TranslationAdmin, ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ProductResource
    list_display = ["name", "sku", "category", "price", "stock", "status", "is_featured", "created_at"]
    list_filter = ["status", "is_featured", "category"]
    list_editable = ["status", "is_featured"]
    search_fields = ["name", "sku"]
    prepopulated_fields = {"slug": ("name",)}
    date_hierarchy = "created_at"
    list_only_fields = ["id", "name", "sku", "category_id", "price", "stock", "status", "is_featured", "created_at"]
    fieldsets = [
        (None, {"fields": ["name", "slug", "description", "category"]}),
        ("Pricing & Stock", {"fields": ["price", "sku", "stock"]}),
        ("Status", {"fields": ["status", "is_featured"]}),
    ]
