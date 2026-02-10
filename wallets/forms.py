# pyright:reportAttributeAccessIssue=false

from django import forms

from .models import Wallet


class WalletCreateForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ("name", "currency")

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "currency": forms.Select(attrs={"class": "form-control"}),
        }


class WalletUpdateForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ("name",)

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
        }


class TransferForm(forms.Form):
    from_wallet = forms.ModelChoiceField(queryset=Wallet.objects.none())
    to_wallet = forms.ModelChoiceField(queryset=Wallet.objects.none())
    amount_from = forms.DecimalField(max_digits=15, decimal_places=2)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["from_wallet"].queryset = user.wallets.all()
        self.fields["to_wallet"].queryset = user.wallets.all()

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("from_wallet") == cleaned.get("to_wallet"):
            raise forms.ValidationError("Cannot transfer to the same wallet")
        return cleaned
