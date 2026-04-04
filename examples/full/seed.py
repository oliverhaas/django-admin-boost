#!/usr/bin/env python
"""Seed the database with example data."""

import os
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

import django

django.setup()

from django.contrib.auth.models import User

from catalog.models import Category, Product

# Superuser
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", "admin")
    print("Created superuser: admin / admin")

# Categories
categories_data = [
    ("Electronics", "electronics", "Gadgets and devices"),
    ("Books", "books", "Physical and digital books"),
    ("Clothing", "clothing", "Apparel and accessories"),
]
categories = {}
for name, slug, desc in categories_data:
    cat, _ = Category.objects.get_or_create(
        slug=slug,
        defaults={"name": name, "description": desc},
    )
    categories[slug] = cat

# Products
products_data = [
    ("Wireless Headphones", "wireless-hp", "WH-100", "electronics", "79.99", 50, "active", True),
    ("USB-C Hub", "usb-c-hub", "UC-200", "electronics", "34.99", 120, "active", False),
    ("Mechanical Keyboard", "mech-kb", "MK-300", "electronics", "129.99", 25, "active", True),
    ("Webcam HD", "webcam-hd", "WC-400", "electronics", "49.99", 0, "archived", False),
    ("Python Cookbook", "py-cookbook", "BK-101", "books", "39.99", 200, "active", False),
    ("Django for Professionals", "django-pro", "BK-102", "books", "44.99", 85, "active", True),
    ("Clean Code", "clean-code", "BK-103", "books", "29.99", 150, "active", False),
    ("Design Patterns", "design-pat", "BK-104", "books", "54.99", 30, "draft", False),
    ("Cotton T-Shirt", "cotton-tee", "CL-201", "clothing", "19.99", 300, "active", False),
    ("Hoodie", "hoodie", "CL-202", "clothing", "49.99", 75, "active", True),
    ("Cap", "cap", "CL-203", "clothing", "14.99", 200, "active", False),
    ("Winter Jacket", "winter-jkt", "CL-204", "clothing", "89.99", 10, "draft", False),
]

for name, slug, sku, cat_slug, price, stock, status, featured in products_data:
    Product.objects.get_or_create(
        sku=sku,
        defaults={
            "name": name,
            "slug": slug,
            "category": categories[cat_slug],
            "price": Decimal(price),
            "stock": stock,
            "status": status,
            "is_featured": featured,
        },
    )

print(
    f"Seeded: {Category.objects.count()} categories, {Product.objects.count()} products",
)
