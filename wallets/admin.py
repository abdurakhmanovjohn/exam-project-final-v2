from django.contrib import admin

from .models import Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "currency", "balance", "created_at")
    list_filter = ("currency",)
    search_fields = ("name", "user__phone_number")
    ordering = ("-created_at",)
