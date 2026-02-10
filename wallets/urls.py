from django.urls import path

from . import views

app_name = "wallets"

urlpatterns = [
    path("", views.wallet_list, name="list"),
    path("create/", views.wallet_create, name="create"),
    path("<int:pk>/edit/", views.wallet_edit, name="edit"),
    path("<int:pk>/delete/", views.wallet_delete, name="delete"),
    path("transfer/", views.transfer_create, name="transfer"),
]
