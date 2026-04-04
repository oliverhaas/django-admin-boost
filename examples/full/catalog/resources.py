from import_export import resources

from .models import Category, Product


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description")
        import_id_fields = ("slug",)


class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        fields = ("id", "name", "slug", "sku", "category__name", "price", "stock", "status", "is_featured")
        import_id_fields = ("sku",)
