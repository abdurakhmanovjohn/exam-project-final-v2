from django import forms
from django.utils.translation import gettext_lazy as _

from .models import User


class PhoneNumberForm(forms.Form):
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "placeholder": "+998 XX XXX XX XX",
                "class": "form-input",
            }
        ),
    )


class VerificationForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={
                "placeholder": "000000",
                "class": "form-input",
            }
        ),
    )


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": _("Password"),
                "class": "form-input",
            }
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": _("Confirm password"),
                "class": "form-input",
            }
        )
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name")
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "placeholder": _("First name"),
                    "class": "form-input",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "placeholder": _("Last name (optional)"),
                    "class": "form-input",
                }
            ),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Passwords do not match"))

        return password2
