#  pyright:reportOperatorIssue=false

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from wallets.models import Wallet

DEFAULT_INCOME_CATEGORIES = [
    "Salary",
    "Freelance",
    "Business",
    "Gift",
]

DEFAULT_EXPENSE_CATEGORIES = [
    "Food",
    "Transport",
    "Rent",
    "Utilities",
    "Internet",
    "Health",
    "Entertainment",
]


class Category(models.Model):
    TYPE_INCOME = "income"
    TYPE_EXPENSE = "expense"

    TYPE_CHOICES = [
        (TYPE_INCOME, _("Income")),
        (TYPE_EXPENSE, _("Expense")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "name", "type")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.type})"


class Income(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={"type": Category.TYPE_INCOME},
    )

    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(
        max_length=3,
        choices=[("UZS", "UZS"), ("USD", "USD"), ("EUR", "EUR")],
    )
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"+{self.amount} {self.currency}"

    def as_transaction(self):
        return {
            "type": "income",
            "details": f"{self.category.name if self.category else 'Income'} → {self.wallet.name}",
            "amount": self.amount,
            "currency": self.currency,
            "date": self.created_at,
        }


class Expense(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={"type": Category.TYPE_EXPENSE},
    )

    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(
        max_length=3,
        choices=[("UZS", "UZS"), ("USD", "USD"), ("EUR", "EUR")],
    )
    date = models.DateField(default=timezone.now())
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"-{self.amount} {self.currency}"

    def as_transaction(self):
        return {
            "type": "expense",
            "details": f"{self.wallet.name} → {self.category.name if self.category else 'Expense'}",
            "amount": -self.amount,
            "currency": self.currency,
            "date": self.created_at,
        }
