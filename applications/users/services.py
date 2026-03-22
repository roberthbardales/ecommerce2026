"""
users/services.py
-----------------
Capa de servicios: aquí vive la lógica de negocio.
Las vistas (CBV) solo orquestan; los servicios ejecutan.
"""
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.models import Cart, CartItem
from .models import Account, UserProfile


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def send_activation_email(request, user: Account) -> None:
    """Envía el correo de activación de cuenta."""
    current_site = get_current_site(request)
    mail_subject = "Please activate your account"
    message = render_to_string(
        "users/account_verification_email.html",
        {
            "user": user,
            "domain": current_site,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
        },
    )
    EmailMessage(mail_subject, message, to=[user.email]).send()


def send_password_reset_email(request, user: Account) -> None:
    """Envía el correo de restablecimiento de contraseña."""
    current_site = get_current_site(request)
    mail_subject = "Reset Your Password"
    message = render_to_string(
        "users/reset_password_email.html",
        {
            "user": user,
            "domain": current_site,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
        },
    )
    EmailMessage(mail_subject, message, to=[user.email]).send()


def decode_uid(uidb64: str) -> Account | None:
    """
    Decodifica un uidb64 y retorna el usuario correspondiente.
    Retorna None si el uid es inválido o el usuario no existe.
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        return Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        return None


def activate_user(user: Account) -> None:
    """Activa la cuenta del usuario."""
    user.is_active = True
    user.save(update_fields=["is_active"])


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register_user(cleaned_data: dict) -> Account:
    """
    Crea un Account + UserProfile a partir de los datos del formulario.
    No envía correos; eso es responsabilidad de la vista/servicio de email.
    """
    email = cleaned_data["email"]
    user = Account.objects.create_user(
        first_name=cleaned_data["first_name"],
        last_name=cleaned_data["last_name"],
        email=email,
        username=email.split("@")[0],
        password=cleaned_data["password"],
    )
    user.phone_number = cleaned_data["phone_number"]
    user.save(update_fields=["phone_number"])

    UserProfile.objects.create(
        user=user,
        profile_picture="default/default-user.png",
    )
    return user


# ---------------------------------------------------------------------------
# Cart merge on login
# ---------------------------------------------------------------------------

def merge_guest_cart_into_user(request, user: Account) -> None:
    """
    Transfiere los ítems del carrito de sesión (guest) al carrito del usuario.
    Si el usuario ya tiene ese ítem (mismas variaciones), incrementa la cantidad.
    Si no, asigna el ítem directamente al usuario.
    """
    from carts.views import _cart_id  # import local para evitar circular

    try:
        guest_cart = Cart.objects.get(cart_id=_cart_id(request))
        guest_items = CartItem.objects.filter(cart=guest_cart)
        if not guest_items.exists():
            return

        # Variaciones actuales del usuario
        user_items = CartItem.objects.filter(user=user)
        existing_variations = [
            list(item.variations.all()) for item in user_items
        ]
        user_item_ids = [item.id for item in user_items]

        for guest_item in guest_items:
            guest_variations = list(guest_item.variations.all())
            if guest_variations in existing_variations:
                idx = existing_variations.index(guest_variations)
                matched = CartItem.objects.get(id=user_item_ids[idx])
                matched.quantity += 1
                matched.user = user
                matched.save(update_fields=["quantity", "user"])
            else:
                guest_item.user = user
                guest_item.save(update_fields=["user"])

    except Cart.DoesNotExist:
        pass


# ---------------------------------------------------------------------------
# Password
# ---------------------------------------------------------------------------

def change_user_password(user: Account, new_password: str) -> None:
    """Cambia la contraseña sin hacer logout."""
    user.set_password(new_password)
    user.save(update_fields=["password"])