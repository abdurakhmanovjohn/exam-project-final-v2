# pyright:reportAttributeAccessIssue=false

from decimal import Decimal

from core.models import ExchangeRate

DEFAULT_RATES = {
    ("USD", "UZS"): Decimal("12650"),
    ("UZS", "USD"): Decimal("0.000079"),
    ("EUR", "UZS"): Decimal("13800"),
    ("UZS", "EUR"): Decimal("0.000072"),
    ("USD", "EUR"): Decimal("0.92"),
    ("EUR", "USD"): Decimal("1.09"),
}


def get_exchange_rate(from_currency: str, to_currency: str) -> Decimal:
    if from_currency == to_currency:
        return Decimal("1")

    rate = DEFAULT_RATES.get((from_currency, to_currency))
    if rate:
        return rate

    reverse = DEFAULT_RATES.get((to_currency, from_currency))
    if reverse:
        return (Decimal("1") / reverse).quantize(Decimal("0.000001"))

    raise ValueError(f"Exchange rate not found: {from_currency} → {to_currency}")


def convert_amount(amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
    rate = get_exchange_rate(from_currency, to_currency)
    return (amount * rate).quantize(Decimal("0.01"))


def convert_to_uzs(amount: Decimal, currency: str) -> Decimal:
    if currency == "UZS":
        return amount
    return convert_amount(amount, currency, "UZS")
