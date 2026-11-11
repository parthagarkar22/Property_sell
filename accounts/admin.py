from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(BaseUserAdmin):
    list_display = ("name", "phone", "is_verified", "is_staff", "created_at")
    list_filter = ("is_verified", "is_staff", "is_active")
    search_fields = ("name", "phone")
    ordering = ("-created_at",)
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Personal", {"fields": ("name", "is_verified")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone", "name", "password1", "password2", "is_staff", "is_superuser"),
            },
        ),
    )
