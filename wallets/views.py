#  pyright: reportAttributeAccessIssue=false

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from .forms import TransferForm, WalletCreateForm, WalletUpdateForm
from .models import Transfer, Wallet
from .services import apply_transfer


@login_required
def wallet_list(request):
    wallets = Wallet.objects.filter(user=request.user)
    return render(request, "wallets/wallet_list.html", {"wallets": wallets})


@login_required
def wallet_create(request):
    if request.method == "POST":
        form = WalletCreateForm(request.POST)
        if form.is_valid():
            wallet = form.save(commit=False)
            wallet.user = request.user
            wallet.save()
            messages.success(request, _("Wallet created successfully"))
            return redirect("wallets:list")
    else:
        form = WalletCreateForm()

    return render(request, "wallets/wallet_form.html", {"form": form})


@login_required
def wallet_edit(request, pk):
    wallet = get_object_or_404(Wallet, pk=pk, user=request.user)

    if wallet.name == "Cash":
        messages.error(request, _("Default wallet name cannot be changed"))
        return redirect("wallets:list")

    if request.method == "POST":
        form = WalletUpdateForm(request.POST, instance=wallet)
        if form.is_valid():
            form.save()
            messages.success(request, _("Wallet name updated"))
            return redirect("wallets:list")
    else:
        form = WalletUpdateForm(instance=wallet)

    return render(
        request,
        "wallets/wallet_edit.html",
        {
            "form": form,
            "wallet": wallet,
        },
    )


@login_required
def wallet_delete(request, pk):
    wallet = get_object_or_404(Wallet, pk=pk, user=request.user)

    if wallet.name == "Cash":
        messages.error(request, _("Default wallet cannot be deleted"))
        return redirect("wallets:list")

    if request.method == "POST":
        wallet.delete()
        messages.success(request, _("Wallet deleted"))
        return redirect("wallets:list")

    return render(request, "wallets/wallet_confirm_delete.html", {"wallet": wallet})


@login_required
@login_required
def transfer_create(request):
    initial = {}
    from_id = request.GET.get("from")
    if from_id:
        try:
            initial["from_wallet"] = Wallet.objects.get(
                id=from_id,
                user=request.user,
            )
        except Wallet.DoesNotExist:
            pass

    if request.method == "POST":
        form = TransferForm(request.user, request.POST)
        if form.is_valid():
            from_wallet = form.cleaned_data["from_wallet"]
            to_wallet = form.cleaned_data["to_wallet"]
            amount = form.cleaned_data["amount_from"]

            try:
                rate, amount_to = apply_transfer(
                    from_wallet=from_wallet,
                    to_wallet=to_wallet,
                    amount=amount,
                )
            except ValueError:
                messages.error(request, _("Insufficient balance"))
                return render(
                    request,
                    "wallets/transfer_form.html",
                    {"form": form},
                )

            Transfer.objects.create(
                user=request.user,
                from_wallet=from_wallet,
                to_wallet=to_wallet,
                amount_from=amount,
                amount_to=amount_to,
                exchange_rate=rate,
            )

            messages.success(request, _("Transfer completed successfully"))
            return redirect("core:dashboard")
    else:
        form = TransferForm(request.user, initial=initial)

    return render(
        request,
        "wallets/transfer_form.html",
        {"form": form},
    )
