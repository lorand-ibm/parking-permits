from django.contrib import admin

from .models import Product, ProductPrice


@admin.register(Product)
class MonitorAdmin(admin.ModelAdmin):
    list_display = ["name", "shared_product_id"]
    ordering = ["name"]
    search_fields = ["name"]


@admin.register(ProductPrice)
class MonitorAdmin(admin.ModelAdmin):
    list_display = ["product", "start_date", "end_date", "price"]
    ordering = ["-start_date"]
