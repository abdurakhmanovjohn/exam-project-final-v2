from django.conf import settings
from django.db import models


class Conversation(models.Model):
  user = models.OneToOneField(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="support_conversation"
  )

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return f"Support chat with {self.user}"


class Message(models.Model):
  conversation = models.ForeignKey(
    Conversation,
    on_delete=models.CASCADE,
    related_name="messages"
  )

  sender = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE
  )

  text = models.TextField()
  is_admin = models.BooleanField(default=False)

  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ["created_at"]

  def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    self.conversation.updated_at = self.created_at
    self.conversation.save(update_fields=["updated_at"])

  def __str__(self):
    return f"{self.sender} - {self.created_at}"
