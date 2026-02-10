from decimal import Decimal

from core.services.currency import get_exchange_rate


def apply_transfer(from_wallet, to_wallet, amount: Decimal):
    if from_wallet.balance < amount:
        raise ValueError("Insufficient balance")

    if from_wallet.currency == to_wallet.currency:
        rate = Decimal("1")
        amount_to = amount
    else:
        rate = get_exchange_rate(from_wallet.currency, to_wallet.currency)
        amount_to = (amount * rate).quantize(Decimal("0.01"))

    from_wallet.balance -= amount
    to_wallet.balance += amount_to

    from_wallet.save(update_fields=["balance"])
    to_wallet.save(update_fields=["balance"])

    return rate, amount_to
