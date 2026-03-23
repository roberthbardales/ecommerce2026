"""
users/views.py
"""
from django.contrib import messages, auth
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import RegistrationForm, UserForm, UserProfileForm
from .mixins import ActiveAccountMixin, StaffRequiredMixin
from .models import Account, UserProfile
from . import services


class RegisterView(View):
    template_name = "users/register.html"

    def get(self, request):
        return render(request, self.template_name, {"form": RegistrationForm()})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = services.register_user(form.cleaned_data)
            services.send_activation_email(request, user)
            return redirect(f"/users/login/?command=verification&email={user.email}")
        return render(request, self.template_name, {"form": form})


class ActivateView(View):
    def get(self, request, uidb64, token):
        user = services.decode_uid(uidb64)
        if user and default_token_generator.check_token(user, token):
            services.activate_user(user)
            messages.success(request, "Your account is now active.")
            return redirect('app_users:login')
        messages.error(request, "Invalid or expired activation link.")
        return redirect('app_users:register')


class LoginView(View):
    template_name = "users/login.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        user = auth.authenticate(request, email=email, password=password)

        if user is None:
            messages.error(request, "Invalid credentials.")
            return render(request, self.template_name)

        # services.merge_guest_cart_into_user(request, user)  # TODO: activar con app carts
        auth.login(request, user)
        messages.success(request, "Welcome back!")

        next_url = request.GET.get("next") or request.POST.get("next")
        return redirect(next_url or 'app_users:dashboard')


class LogoutView(ActiveAccountMixin, View):
    login_url = 'app_users:login'

    def get(self, request):
        auth.logout(request)
        messages.success(request, "You have been logged out.")
        return redirect('app_users:login')


class ForgotPasswordView(View):
    template_name = "users/forgot_password.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get("email", "").strip()
        try:
            user = Account.objects.get(email__iexact=email)
        except Account.DoesNotExist:
            messages.error(request, "No account found with that email.")
            return redirect('app_users:forgot_password')

        services.send_password_reset_email(request, user)
        messages.success(request, "Password reset link sent.")
        return redirect('app_users:login')


class ResetPasswordValidateView(View):
    def get(self, request, uidb64, token):
        user = services.decode_uid(uidb64)
        if user and default_token_generator.check_token(user, token):
            request.session["reset_uid"] = str(user.pk)
            return redirect('app_users:reset_password')
        messages.error(request, "This link has expired.")
        return redirect('app_users:login')


class ResetPasswordView(View):
    template_name = "users/reset_password.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm_password", "")

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('app_users:reset_password')

        uid = request.session.get("reset_uid")
        if not uid:
            messages.error(request, "Session expired.")
            return redirect('app_users:forgot_password')

        try:
            user = Account.objects.get(pk=uid)
        except Account.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('app_users:forgot_password')

        services.change_user_password(user, password)
        del request.session["reset_uid"]
        messages.success(request, "Password changed successfully.")
        return redirect('app_users:login')


class DashboardView(ActiveAccountMixin, View):
    login_url = 'app_users:login'
    template_name = "users/dashboard.html"

    def get(self, request):
        userprofile = get_object_or_404(UserProfile, user=request.user)
        return render(request, self.template_name, {
            "orders_count": 0,  # TODO: activar con app orders
            "userprofile": userprofile,
        })


class MyOrdersView(ActiveAccountMixin, View):
    login_url = 'app_users:login'
    template_name = "users/my_orders.html"

    def get(self, request):
        return render(request, self.template_name, {"orders": []})  # TODO: activar con app orders


class OrderDetailView(ActiveAccountMixin, View):
    login_url = 'app_users:login'
    template_name = "users/order_detail.html"

    def get(self, request, order_id):
        return render(request, self.template_name, {
            "order": None,
            "order_detail": [],
            "subtotal": 0,
        })  # TODO: activar con app orders


class EditProfileView(ActiveAccountMixin, View):
    login_url = 'app_users:login'
    template_name = "users/edit_profile.html"

    def _forms(self, request, userprofile, data=None, files=None):
        return (
            UserForm(data, instance=request.user),
            UserProfileForm(data, files, instance=userprofile),
        )

    def get(self, request):
        userprofile = get_object_or_404(UserProfile, user=request.user)
        user_form, profile_form = self._forms(request, userprofile)
        return render(request, self.template_name, {
            "user_form": user_form,
            "profile_form": profile_form,
            "userprofile": userprofile,
        })

    def post(self, request):
        userprofile = get_object_or_404(UserProfile, user=request.user)
        user_form, profile_form = self._forms(
            request, userprofile, request.POST, request.FILES
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated.")
            return redirect('app_users:edit_profile')
        return render(request, self.template_name, {
            "user_form": user_form,
            "profile_form": profile_form,
            "userprofile": userprofile,
        })


class ChangePasswordView(ActiveAccountMixin, View):
    login_url = 'app_users:login'
    template_name = "users/change_password.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        current = request.POST.get("current_password", "")
        new_pw = request.POST.get("new_password", "")
        confirm = request.POST.get("confirm_password", "")

        if new_pw != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('app_users:change_password')

        if not request.user.check_password(current):
            messages.error(request, "Current password is incorrect.")
            return redirect('app_users:change_password')

        services.change_user_password(request.user, new_pw)
        messages.success(request, "Password updated successfully.")
        return redirect('app_users:change_password')