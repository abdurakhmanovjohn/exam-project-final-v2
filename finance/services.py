from decimal import Decimal

from core.services.currency import convert_amount


def apply_income(wallet, amount: Decimal, currency: str):
    converted = convert_amount(amount, currency, wallet.currency)
    wallet.balance += converted
    wallet.save(update_fields=["balance"])


def apply_expense(wallet, amount: Decimal, currency: str):
    converted = convert_amount(amount, currency, wallet.currency)

    if wallet.balance < converted:
        raise ValueError("Insufficient balance")

    wallet.balance -= converted
    wallet.save(update_fields=["balance"])
