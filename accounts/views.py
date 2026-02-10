# pyright: reportAttributeAccessIssue=false

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from finance.models import (
    DEFAULT_EXPENSE_CATEGORIES,
    DEFAULT_INCOME_CATEGORIES,
    Category,
)

from .forms import PhoneNumberForm, RegistrationForm, VerificationForm
from .models import User
from .services import create_and_send_otp, verify_otp


def register_phone(request):
    if request.method == "POST":
        form = PhoneNumberForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data["phone_number"]

            if User.objects.filter(phone_number=phone).exists():
                messages.error(request, _("Phone already registered"))
                return redirect("accounts:login")

            create_and_send_otp(phone)
            request.session["phone_number"] = phone
            return redirect("accounts:verify_phone")
    else:
        form = PhoneNumberForm()

    return render(request, "accounts/register_phone.html", {"form": form})


def verify_phone(request):
    phone = request.session.get("phone_number")
    if not phone:
        return redirect("accounts:register_phone")

    if request.method == "POST":
        form = VerificationForm(request.POST)
        if form.is_valid():
            if verify_otp(phone, form.cleaned_data["code"]):
                request.session["verified_phone"] = phone
                return redirect("accounts:complete")
            messages.error(request, _("Invalid or expired code"))
    else:
        form = VerificationForm()

    return render(request, "accounts/verify_phone.html", {"form": form})


def register_complete(request):
    phone = request.session.get("verified_phone")
    if not phone:
        return redirect("accounts:register_phone")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.phone_number = phone
            user.set_password(form.cleaned_data["password1"])
            user.save()

            for name in DEFAULT_INCOME_CATEGORIES:
                Category.objects.create(
                    user=user,
                    name=name,
                    type="income",
                )

            for name in DEFAULT_EXPENSE_CATEGORIES:
                Category.objects.create(
                    user=user,
                    name=name,
                    type="expense",
                )

            request.session.pop("phone_number", None)
            request.session.pop("verified_phone", None)

            login(request, user)
            return redirect("core:dashboard")
    else:
        form = RegistrationForm()

    return render(
        request,
        "accounts/register_complete.html",
        {
            "form": form,
            "phone_number": phone,
        },
    )


def user_login(request):
    if request.method == "POST":
        phone = request.POST.get("phone_number")
        password = request.POST.get("password")

        user = authenticate(request, username=phone, password=password)
        if user:
            login(request, user)
            return redirect("core:dashboard")

        messages.error(request, _("Invalid credentials"))

    return render(request, "accounts/login.html")


def user_logout(request):
    logout(request)
    return redirect("accounts:login")
