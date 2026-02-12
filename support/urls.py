from django.urls import path
from . import views

app_name = "support"

urlpatterns = [
    path("", views.support_chat, name="chat"),

    path("admin/", views.admin_conversations, name="admin_conversations"),
    path("admin/<int:conversation_id>/", views.admin_chat_detail, name="admin_chat_detail"),
]