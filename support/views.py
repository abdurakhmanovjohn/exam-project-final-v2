from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
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