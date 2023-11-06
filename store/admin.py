from django.contrib import admin
from .models import Brand, Group, Product, Order


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "brand", "price_per_gram", "gender"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["user", "phone", "address", "completed", "ordered_at", "price"]
    actions = ["complete_order"]

    @admin.action(description="Sifarişi tamamla")
    def complete_order(modeladmin, request, queryset):
        for obj in queryset:
            obj.complete()
