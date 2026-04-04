from modeltranslation.translator import TranslationOptions, register

from .models import Category, Product


@register(Category)
class CategoryTranslation(TranslationOptions):
    fields = ("name", "description")


@register(Product)
class ProductTranslation(TranslationOptions):
    fields = ("name", "description")
