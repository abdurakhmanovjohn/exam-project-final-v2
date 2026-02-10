from django.db import models
from django.utils.translation import gettext_lazy as _


class ExchangeRate(models.Model):
    CURRENCY_CHOICES = [
        ("UZS", "UZS"),
        ("USD", "USD"),
        ("EUR", "EUR"),
    ]

    from_currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
    )
    to_currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
    )
    rate = models.DecimalField(
        max_digits=15,
        decimal_places=6,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("from_currency", "to_currency")
        verbose_name = _("exchange rate")
        verbose_name_plural = _("exchange rates")

    def __str__(self):
        return f"{self.from_currency} → {self.to_currency} = {self.rate}"
