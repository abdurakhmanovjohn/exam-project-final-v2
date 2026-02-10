from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register_phone, name="register_phone"),
    path("verify/", views.verify_phone, name="verify_phone"),
    path("complete/", views.register_complete, name="complete"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
]
