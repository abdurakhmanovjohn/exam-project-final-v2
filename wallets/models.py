from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

User = settings.AUTH_USER_MODEL


class Wallet(models.Model):
    CURRENCY_CHOICES = [
        ("UZS", _("Uzbek Som")),
        ("USD", _("US Dollar")),
        ("EUR", _("Euro")),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="wallets",
    )
    name = models.CharField(_("wallet name"), max_length=100)
    currency = models.CharField(
        _("currency"),
        max_length=3,
        choices=CURRENCY_CHOICES,
        default="UZS",
    )
    balance = models.DecimalField(
        _("balance"),
        max_digits=20,
        decimal_places=2,
        default=0,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("wallet")
        verbose_name_plural = _("wallets")
        unique_together = ("user", "name")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.currency})"


class Transfer(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transfers",
    )

    from_wallet = models.ForeignKey(
        "wallets.Wallet",
        on_delete=models.CASCADE,
        related_name="outgoing_transfers",
    )
    to_wallet = models.ForeignKey(
        "wallets.Wallet",
        on_delete=models.CASCADE,
        related_name="incoming_transfers",
    )

    amount_from = models.DecimalField(max_digits=15, decimal_places=2)
    amount_to = models.DecimalField(max_digits=15, decimal_places=2)
    exchange_rate = models.DecimalField(max_digits=15, decimal_places=6)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.from_wallet} → {self.to_wallet}"

    def as_transaction(self):
        return {
            "type": "transfer",
            "details": f"{self.from_wallet.name} → {self.to_wallet.name}",
            "amount": self.amount_from,
            "currency": self.from_wallet.currency,
            "date": self.created_at,
        }
