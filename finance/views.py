# pyright: reportAttributeAccessIssue=false


from core.services.currency import convert_amount
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Expense, Income

from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from finance.models import Category, Expense, Income
from wallets.models import Transfer

from .forms import CategoryForm, ExpenseForm, IncomeForm, TransactionFilterForm
from .models import Expense, Income
from .services import apply_expense, apply_income


@login_required
def income_create(request):
    if request.method == "POST":
        form = IncomeForm(request.user, request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()

            apply_income(income.wallet, income.amount, income.currency)

            messages.success(request, "Income added")
            return redirect("core:dashboard")
    else:
        form = IncomeForm(request.user)

    return render(request, "finance/income_form.html", {"form": form})


@login_required
def expense_create(request):
    if request.method == "POST":
        form = ExpenseForm(request.user, request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user

            try:
                apply_expense(expense.wallet, expense.amount, expense.currency)
            except ValueError:
                messages.error(request, "Insufficient balance")
                return render(request, "finance/expense_form.html", {"form": form})

            expense.save()
            messages.success(request, "Expense added")
            return redirect("core:dashboard")
    else:
        form = ExpenseForm(request.user)

    return render(request, "finance/expense_form.html", {"form": form})


@login_required
def category_list(request, category_type):
    categories = Category.objects.filter(
        user=request.user,
        type=category_type,
    )

    return render(
        request,
        "finance/category_list.html",
        {
            "categories": categories,
            "category_type": category_type,
        },
    )


@login_required
def category_create(request, category_type):
    if category_type not in ("income", "expense"):
        return redirect("core:dashboard")

    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.type = category_type

            if Category.objects.filter(
                user=request.user,
                name=category.name,
                type=category_type,
            ).exists():
                messages.error(request, "Category with this name already exists.")
            else:
                category.save()
                messages.success(request, "Category created")
                return redirect(
                    "finance:categories",
                    category_type=category_type,
                )
    else:
        form = CategoryForm()

    return render(
        request,
        "finance/category_form.html",
        {
            "form": form,
            "category_type": category_type,
        },
    )


@login_required
def category_edit(request, pk):
    category = get_object_or_404(
        Category,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated")
            return redirect(
                "finance:categories",
                category_type=category.type,
            )
    else:
        form = CategoryForm(instance=category)

    return render(
        request,
        "finance/category_form.html",
        {
            "form": form,
            "category_type": category.type,
        },
    )


@login_required
def category_delete(request, pk):
    category = get_object_or_404(
        Category,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted")
        return redirect(
            "finance:categories",
            category_type=category.type,
        )

    return render(
        request,
        "finance/category_confirm_delete.html",
        {
            "category": category,
        },
    )


@login_required
def reports(request):
    report_type = request.GET.get("type", "all")
    period = request.GET.get("period", "monthly")
    base_currency = request.GET.get("currency", "UZS")

    today = timezone.now().date()

    if period == "daily":
        start_date = today
        end_date = today

    elif period == "weekly":
        start_date = today - timedelta(days=7)
        end_date = today

    elif period == "monthly":
        start_date = today.replace(day=1)
        end_date = today

    elif period == "custom":
        try:
            start_date = datetime.strptime(
                request.GET.get("start"), "%Y-%m-%d"
            ).date()
            end_date = datetime.strptime(
                request.GET.get("end"), "%Y-%m-%d"
            ).date()
        except (TypeError, ValueError):
            start_date = None
            end_date = None
    else:
        start_date = None
        end_date = None

    incomes = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)

    if start_date and end_date:
        incomes = incomes.filter(date__range=(start_date, end_date))
        expenses = expenses.filter(date__range=(start_date, end_date))

    income_total = 0
    expense_total = 0

    income_by_category = {}
    expense_by_category = {}

    for inc in incomes:
        converted = convert_amount(
            inc.amount, inc.currency, base_currency
        )
        income_total += converted
        key = inc.category.name if inc.category else "Other"
        income_by_category[key] = income_by_category.get(key, 0) + converted

    for exp in expenses:
        converted = convert_amount(
            exp.amount, exp.currency, base_currency
        )
        expense_total += converted
        key = exp.category.name if exp.category else "Other"
        expense_by_category[key] = expense_by_category.get(key, 0) + converted

    net = income_total - expense_total

    def build_percentage(data_dict, total):
        result = []
        for name, amount in data_dict.items():
            percent = (amount / total * 100) if total else 0
            result.append(
                {
                    "category": name,
                    "amount": round(amount, 2),
                    "percent": round(percent, 1),
                }
            )
        return sorted(result, key=lambda x: x["amount"], reverse=True)

    income_data = build_percentage(income_by_category, income_total)
    expense_data = build_percentage(expense_by_category, expense_total)

    return render(
        request,
        "finance/reports.html",
        {
            "income_total": round(income_total, 2),
            "expense_total": round(expense_total, 2),
            "net": round(net, 2),
            "income_data": income_data,
            "expense_data": expense_data,
            "period": period,
            "base_currency": base_currency,
            "start": request.GET.get("start", ""),
            "end": request.GET.get("end", ""),
        },
    )


@login_required
def transaction_list(request):

    form = TransactionFilterForm(request.user, request.GET)

    incomes = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)
    transfers = Transfer.objects.filter(user=request.user)

    if form.is_valid():
        tx_type = form.cleaned_data.get("tx_type")
        wallet = form.cleaned_data.get("wallet")
        date_from = form.cleaned_data.get("date_from")
        date_to = form.cleaned_data.get("date_to")

        if wallet:
            incomes = incomes.filter(wallet=wallet)
            expenses = expenses.filter(wallet=wallet)
            transfers = transfers.filter(from_wallet=wallet) | transfers.filter(
                to_wallet=wallet
            )

        if date_from:
            incomes = incomes.filter(date__gte=date_from)
            expenses = expenses.filter(date__gte=date_from)
            transfers = transfers.filter(date__gte=date_from)

        if date_to:
            incomes = incomes.filter(date__lte=date_to)
            expenses = expenses.filter(date__lte=date_to)
            transfers = transfers.filter(date__lte=date_to)

    transactions = []

    if not form.cleaned_data.get("tx_type") or form.cleaned_data["tx_type"] == "income":
        for i in incomes:
            i.tx_type = "income"
            transactions.append(i)

    if (
        not form.cleaned_data.get("tx_type")
        or form.cleaned_data["tx_type"] == "expense"
    ):
        for e in expenses:
            e.tx_type = "expense"
            transactions.append(e)

    if (
        not form.cleaned_data.get("tx_type")
        or form.cleaned_data["tx_type"] == "transfer"
    ):
        for t in transfers:
            t.tx_type = "transfer"
            transactions.append(t)

    transactions.sort(key=lambda x: x.date, reverse=True)

    return render(
        request,
        "finance/transaction_list.html",
        {
            "transactions": transactions,
            "form": form,
        },
    )
