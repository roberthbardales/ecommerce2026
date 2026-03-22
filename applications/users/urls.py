"""
users/urls.py
"""
from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    # Auth
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),

    # Activation
    path("activate/<uidb64>/<token>/", views.ActivateView.as_view(), name="activate"),

    # Password reset
    path("forgot-password/", views.ForgotPasswordView.as_view(), name="forgot_password"),
    path(
        "reset-password-validate/<uidb64>/<token>/",
        views.ResetPasswordValidateView.as_view(),
        name="reset_password_validate",
    ),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset_password"),

    # Dashboard & profile
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("my-orders/", views.MyOrdersView.as_view(), name="my_orders"),
    path("order/<int:order_id>/", views.OrderDetailView.as_view(), name="order_detail"),
    path("edit-profile/", views.EditProfileView.as_view(), name="edit_profile"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change_password"),
]