# pyright: reportAttributeAccessIssue=false

from django import forms

from wallets.models import Wallet

from .models import Category, Expense, Income


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ("wallet", "category", "amount", "currency", "date")

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["wallet"].queryset = user.wallets.all()
        self.fields["category"].queryset = Category.objects.filter(
            user=user, type=Category.TYPE_INCOME
        )


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ("wallet", "category", "amount", "currency", "date")

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["wallet"].queryset = user.wallets.all()
        self.fields["category"].queryset = Category.objects.filter(
            user=user, type=Category.TYPE_EXPENSE
        )


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name",)


class TransactionFilterForm(forms.Form):
    TYPE_CHOICES = (
        ("", "All"),
        ("income", "Income"),
        ("expense", "Expense"),
        ("transfer", "Transfer"),
    )

    tx_type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    wallet = forms.ModelChoiceField(
        queryset=Wallet.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["wallet"].queryset = user.wallets.all()
