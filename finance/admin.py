from django.contrib import admin

from .models import Category, Expense, Income


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "user")
    list_filter = ("type",)
    search_fields = ("name", "user__phone_number")


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "currency", "wallet", "date")
    list_filter = ("currency", "date")
    ordering = ("-date",)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "currency", "wallet", "date")
    list_filter = ("currency", "date")
    ordering = ("-date",)
