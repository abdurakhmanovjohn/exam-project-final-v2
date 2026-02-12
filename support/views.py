from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import Conversation, Message
from .forms import MessageForm


@login_required
def support_chat(request):
    conversation, _ = Conversation.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.is_admin = False
            message.save()
            return redirect("support:chat")
    else:
        form = MessageForm()

    messages = conversation.messages.select_related("sender")

    return render(
        request,
        "support/chat.html",
        {
            "conversation": conversation,
            "messages": messages,
            "form": form,
        },
    )


def is_admin(user):
    return user.is_staff


@user_passes_test(is_admin)
def admin_conversations(request):
    conversations = Conversation.objects.select_related("user").order_by("-updated_at")

    return render(
        request,
        "support/admin_conversations.html",
        {
            "conversations": conversations,
        },
    )


@user_passes_test(is_admin)
def admin_chat_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.is_admin = True
            message.save()
            return redirect("support:admin_chat_detail", conversation_id=conversation.id)
    else:
        form = MessageForm()

    messages = conversation.messages.select_related("sender")

    return render(
        request,
        "support/admin_chat.html",
        {
            "conversation": conversation,
            "messages": messages,
            "form": form,
        },
    )