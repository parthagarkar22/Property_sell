from django.contrib import admin

from .models import Interest, Property, PropertyImage


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ("image", "is_primary", "order")


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "area",
        "property_type",
        "deal_status",
        "sq_ft",
        "price_per_sq_ft",
        "total_price",
        "is_active",
        "is_featured",
        "created_at",
    )
    list_filter = ("deal_status", "property_type", "area", "is_active", "is_featured")
    search_fields = ("title", "location_detail", "description")
    list_editable = ("deal_status", "is_active", "is_featured")
    inlines = [PropertyImageInline]
    fieldsets = (
        (
            "Basic",
            {
                "fields": (
                    "title",
                    "description",
                    "property_type",
                    "deal_status",
                    "is_active",
                    "is_featured",
                )
            },
        ),
        ("Location (Vidarbha)", {"fields": ("area", "location_detail", "maps_url")}),
        ("Size & Price", {"fields": ("sq_ft", "acres", "bhk", "price_per_sq_ft", "total_price")}),
        ("Media", {"fields": ("youtube_url",)}),
    )


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "customer_phone", "property", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("customer__name", "customer__phone", "property__title")
    list_editable = ("status",)
    readonly_fields = ("customer", "property", "created_at", "updated_at")
    ordering = ("-created_at",)

    @admin.display(description="Name", ordering="customer__name")
    def customer_name(self, obj):
        return obj.customer.name

    @admin.display(description="Phone", ordering="customer__phone")
    def customer_phone(self, obj):
        return obj.customer.phone
