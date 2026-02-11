# pyright: reportAttributeAccessIssue=false


import base64
import io
from datetime import timedelta

import matplotlib
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone

from .models import Expense, Income

matplotlib.use("Agg")
import base64
import io
from datetime import datetime, timedelta
from itertools import chain

import matplotlib
import matplotlib.pyplot as plt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from finance.models import Category, Expense, Income
from wallets.models import Transfer

from .forms import CategoryForm, ExpenseForm, IncomeForm, TransactionFilterForm
from .models import Expense, Income
from .services import apply_expense, apply_income

matplotlib.use("Agg")


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
    report_type = request.GET.get("type", "income")
    period = request.GET.get("period", "monthly")

    today = timezone.now().date()
    start_date = None
    end_date = None

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
            start_date = timezone.datetime.strptime(
                request.GET.get("start"), "%Y-%m-%d"
            ).date()
            end_date = timezone.datetime.strptime(
                request.GET.get("end"), "%Y-%m-%d"
            ).date()
        except (TypeError, ValueError):
            start_date = None
            end_date = None

    model = Income if report_type == "income" else Expense
    qs = model.objects.filter(user=request.user)

    if start_date and end_date:
        qs = qs.filter(date__range=(start_date, end_date))

    qs = qs.values("category__name").annotate(total=Sum("amount")).order_by("-total")

    total_amount = sum(item["total"] for item in qs) or 0

    report_data = []
    for item in qs:
        percent = (item["total"] / total_amount * 100) if total_amount else 0
        report_data.append(
            {
                "category": item["category__name"] or "Other",
                "amount": item["total"],
                "percent": round(percent, 1),
            }
        )

    return render(
        request,
        "finance/reports.html",
        {
            "report_type": report_type,
            "period": period,
            "data": report_data,
            "total": total_amount,
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
            incomes = incomes.filter(created_at__date__gte=date_from)
            expenses = expenses.filter(created_at__date__gte=date_from)
            transfers = transfers.filter(created_at__date__gte=date_from)

        if date_to:
            incomes = incomes.filter(created_at__date__lte=date_to)
            expenses = expenses.filter(created_at__date__lte=date_to)
            transfers = transfers.filter(created_at__date__lte=date_to)

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

    transactions.sort(key=lambda x: x.created_at, reverse=True)

    return render(
        request,
        "finance/transaction_list.html",
        {
            "transactions": transactions,
            "form": form,
        },
    )
