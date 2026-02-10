from django.urls import path

from . import views

app_name = "finance"

urlpatterns = [
    path("income/create/", views.income_create, name="income_create"),
    path("expense/create/", views.expense_create, name="expense_create"),
    path("categories/<str:category_type>/", views.category_list, name="categories"),
    path(
        "categories/<str:category_type>/create/",
        views.category_create,
        name="category_create",
    ),
    path("categories/edit/<int:pk>/", views.category_edit, name="category_edit"),
    path("categories/delete/<int:pk>/", views.category_delete, name="category_delete"),
    path("reports/", views.reports, name="reports"),
    path("transactions/", views.transaction_list, name="transactions"),
]
