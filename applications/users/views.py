"""
users/views.py
"""
from django.contrib import messages, auth
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import RegistrationForm, UserForm, UserProfileForm
from .mixins import ActiveAccountMixin, StaffRequiredMixin
from applications.orders.models import Order
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
            messages.success(request, "Tu cuenta ya está activa.")
            return redirect('app_users:login')
        messages.error(request, "Enlace de activación inválido o expirado.")
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
            messages.error(request, "Credenciales inválidas")
            return render(request, self.template_name)

        # services.merge_guest_cart_into_user(request, user)  # TODO: activar con app carts
        auth.login(request, user)
        messages.success(request, "¡Bienvenido de nuevo!")

        next_url = request.GET.get("next") or request.POST.get("next")
        return redirect(next_url or 'app_users:dashboard')


class LogoutView(ActiveAccountMixin, View):
    login_url = 'app_users:login'

    def get(self, request):
        auth.logout(request)
        messages.success(request, "Has cerrado sesión.")
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
            messages.error(request, "No se encontró ninguna cuenta con ese correo electrónico")
            return redirect('app_users:forgot_password')

        services.send_password_reset_email(request, user)
        messages.success(request, "Se ha enviado el enlace para restablecer la contraseña")
        return redirect('app_users:login')


class ResetPasswordValidateView(View):
    def get(self, request, uidb64, token):
        user = services.decode_uid(uidb64)
        if user and default_token_generator.check_token(user, token):
            request.session["reset_uid"] = str(user.pk)
            return redirect('app_users:reset_password')
        messages.error(request, "Este enlace ha expirado.")
        return redirect('app_users:login')


class ResetPasswordView(View):
    template_name = "users/reset_password.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm_password", "")

        if password != confirm:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('app_users:reset_password')

        uid = request.session.get("reset_uid")
        if not uid:
            messages.error(request, "La sesión ha expirado.")
            return redirect('app_users:forgot_password')

        try:
            user = Account.objects.get(pk=uid)
        except Account.DoesNotExist:
            messages.error(request, "Usuario no encontrado")
            return redirect('app_users:forgot_password')

        services.change_user_password(user, password)
        del request.session["reset_uid"]
        messages.success(request, "La contraseña se ha cambiado correctamente")
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
        orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
        return render(request, self.template_name, {"orders": orders})


from applications.orders.models import Order, OrderProduct
from django.shortcuts import render, get_object_or_404
...
class OrderDetailView(ActiveAccountMixin, View):
    login_url = 'app_users:login'
    template_name = "users/order_detail.html"

    def get(self, request, order_id):
        order = get_object_or_404(Order, order_number=order_id, user=request.user)
        order_detail = OrderProduct.objects.filter(order=order)
        
        subtotal = 0
        for i in order_detail:
            subtotal += i.product_price * i.quantity

        return render(request, self.template_name, {
            "order": order,
            "order_detail": order_detail,
            "subtotal": subtotal,
        })


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
            messages.success(request, "Perfil actualizado.")
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
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('app_users:change_password')

        if not request.user.check_password(current):
            messages.error(request, "La contraseña actual es incorrecta.")
            return redirect('app_users:change_password')

        services.change_user_password(request.user, new_pw)
        messages.success(request, "Contraseña actualizada correctamente.")
        return redirect('app_users:change_password')