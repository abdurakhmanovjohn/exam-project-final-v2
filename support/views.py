# pyright: reportAttributeAccessIssue=false

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SupportMessageForm, SupportTicketForm
from .models import SupportMessage, SupportTicket


@login_required
def ticket_list(request):
    tickets = SupportTicket.objects.filter(user=request.user)
    return render(request, "support/ticket_list.html", {"tickets": tickets})


@login_required
def ticket_create(request):
    if request.method == "POST":
        ticket_form = SupportTicketForm(request.POST)
        message_form = SupportMessageForm(request.POST)

        if ticket_form.is_valid() and message_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()

            SupportMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                message=message_form.cleaned_data["message"],
                is_admin=False,
            )

            messages.success(request, "Support ticket created")
            return redirect("support:ticket_detail", ticket.id)
    else:
        ticket_form = SupportTicketForm()
        message_form = SupportMessageForm()

    return render(
        request,
        "support/ticket_form.html",
        {
            "ticket_form": ticket_form,
            "message_form": message_form,
        },
    )


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(SupportTicket, pk=pk, user=request.user)
    messages_qs = ticket.messages.all()

    if request.method == "POST":
        form = SupportMessageForm(request.POST)
        if form.is_valid():
            SupportMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                message=form.cleaned_data["message"],
                is_admin=False,
            )
            ticket.status = SupportTicket.STATUS_OPEN
            ticket.save()
            return redirect("support:ticket_detail", pk)
    else:
        form = SupportMessageForm()

    return render(
        request,
        "support/ticket_detail.html",
        {
            "ticket": ticket,
            "messages": messages_qs,
            "form": form,
        },
    )
