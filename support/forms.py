from django import forms

from .models import SupportMessage, SupportTicket


class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ("subject",)
        widgets = {
            "subject": forms.TextInput(
                attrs={"class": "input", "placeholder": "Briefly describe your issue"}
            )
        }


class SupportMessageForm(forms.ModelForm):
    class Meta:
        model = SupportMessage
        fields = ("message",)
        widgets = {
            "message": forms.Textarea(
                attrs={
                    "class": "input",
                    "rows": 4,
                    "placeholder": "Write your message…",
                }
            )
        }
