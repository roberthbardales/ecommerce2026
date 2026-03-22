"""
users/mixins.py
---------------
Mixins de permisos reutilizables.
Se colocan ANTES de View en el MRO (Method Resolution Order):

    class MyView(StaffRequiredMixin, View): ...

Django's AccessMixin ya provee:
  - login_url
  - raise_exception
  - get_login_url()
  - handle_no_permission()
"""
from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied


# ---------------------------------------------------------------------------
# 1. Usuario autenticado + cuenta activa
#    Úsalo en vistas de usuario normal (perfil, órdenes, etc.)
# ---------------------------------------------------------------------------
class ActiveAccountMixin(AccessMixin):
    """
    Requiere que el usuario esté logueado Y que su cuenta esté activa.
    Si no está autenticado  → redirige a login_url.
    Si está auth pero inactivo → 403 PermissionDenied.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_active:
            raise PermissionDenied("Your account is not active.")
        return super().dispatch(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# 2. Staff (admin del sitio)
#    Úsalo en vistas de gestión interna.
# ---------------------------------------------------------------------------
class StaffRequiredMixin(AccessMixin):
    """
    Requiere is_staff = True.
    Si no está autenticado  → redirige a login.
    Si está auth pero no es staff → 403.
    """
    raise_exception = True  # devuelve 403 en vez de redirigir a login

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_staff:
            raise PermissionDenied("Staff access required.")
        return super().dispatch(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# 3. Superusuario
#    Para vistas críticas (configuración, danger zone).
# ---------------------------------------------------------------------------
class SuperuserRequiredMixin(AccessMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_superuser:
            raise PermissionDenied("Superuser access required.")
        return super().dispatch(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# 4. Genérico: basado en atributos del usuario
#    Evita crear un mixin nuevo por cada rol custom.
#
#    Uso:
#        class MyView(UserPassesTestMixin, View):
#            def test_func(self):
#                return self.request.user.groups.filter(name='Sellers').exists()
#
#    O con el mixin propio para checks simples de atributo:
#        class MyView(UserAttributeMixin, View):
#            required_attribute = 'is_verified'   # cualquier campo bool del modelo
# ---------------------------------------------------------------------------
class UserAttributeMixin(AccessMixin):
    """
    Verifica que request.user.<required_attribute> sea truthy.
    Configura `required_attribute` en la vista hija.
    """
    required_attribute: str = ""
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not self.required_attribute:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} requires 'required_attribute'."
            )
        if not getattr(request.user, self.required_attribute, False):
            raise PermissionDenied(
                f"Missing permission: {self.required_attribute}"
            )
        return super().dispatch(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# 5. El usuario solo puede acceder a sus propios recursos
#    Útil para order_detail, edit_profile, etc.
#    Lanza 403 si el objeto no pertenece al usuario actual.
# ---------------------------------------------------------------------------
class OwnershipMixin:
    """
    Mixin para CBVs con get_object().
    Verifica que obj.<owner_field> == request.user.
    Combínalo con LoginRequiredMixin o ActiveAccountMixin.

    Ejemplo:
        class OrderDetailView(ActiveAccountMixin, OwnershipMixin, DetailView):
            model = Order
            owner_field = 'user'   # campo FK en Order que apunta a Account
    """
    owner_field: str = "user"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        owner = getattr(obj, self.owner_field, None)
        if owner != self.request.user:
            raise PermissionDenied("You don't have access to this resource.")
        return obj