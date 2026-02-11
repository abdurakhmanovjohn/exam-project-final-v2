from django.contrib import admin
from .models import Conversation, Message


class MessageInline(admin.TabularInline):
  model = Message
  extra = 1
  fields = ["text", "is_admin"]
  readonly_fields = ["created_at"]

  def save_new(self, form, commit=True):
    obj = super().save_new(form, commit=False)
    obj.is_admin = True
    obj.sender = form.request.user
    if commit:
      obj.save()
    return obj


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
  list_display = ["user", "updated_at"]
  inlines = [MessageInline]

  def save_formset(self, request, form, formset, change):
    instances = formset.save(commit=False)
    for instance in instances:
      instance.sender = request.user
      instance.is_admin = True
      instance.save()
    formset.save_m2m()