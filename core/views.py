# pyright: reportAttributeAccessIssue=false

from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from core.services.currency import convert_to_uzs
from finance.models import Expense, Income
from wallets.models import Wallet


@login_required
def dashboard(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    total_balance_uzs = 0
    wallets = Wallet.objects.filter(user=request.user)

    for wallet in wallets:
        total_balance_uzs += convert_to_uzs(wallet.balance, wallet.currency)

    income_total_uzs = 0
    incomes = Income.objects.filter(
        user=request.user,
        created_at__gte=month_start,
    )

    for income in incomes:
        income_total_uzs += convert_to_uzs(income.amount, income.currency)

    expense_total_uzs = 0
    expenses = Expense.objects.filter(
        user=request.user,
        created_at__gte=month_start,
    )

    for expense in expenses:
        expense_total_uzs += convert_to_uzs(expense.amount, expense.currency)

    return render(
        request,
        "core/dashboard.html",
        {
            "wallets": wallets,
            "total_balance": total_balance_uzs,
            "income_total": income_total_uzs,
            "expense_total": expense_total_uzs,
            "base_currency": "UZS",
        },
    )
