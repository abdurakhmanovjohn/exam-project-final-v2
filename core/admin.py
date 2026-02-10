from django.contrib import admin

from .models import ExchangeRate


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ("from_currency", "to_currency", "rate", "updated_at")
    list_filter = ("from_currency", "to_currency")
    ordering = ("from_currency", "to_currency")
