from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, VerificationCode


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("phone_number",)
    list_display = ("phone_number", "first_name", "is_staff")

    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("Personal", {"fields": ("first_name", "last_name", "language")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser")}),
    )


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "code", "created_at", "is_used")
