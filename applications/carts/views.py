"""
Carts views — CBV con capa de servicios.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import View, TemplateView

from . import services


# ---------------------------------------------------------------------------
# Helper de redirect — mantiene compatibilidad con el context_processor
# ---------------------------------------------------------------------------

def _get_cart_id(request):
    """Expuesto para que store/product_detail pueda verificar in_cart."""
    return services.get_cart_id(request)


# ---------------------------------------------------------------------------
# Add to cart
# ---------------------------------------------------------------------------

class AddCartView(View):
    def post(self, request, product_id):
        services.add_item_to_cart(request, product_id)
        return redirect('app_carts:cart')

    # GET también redirige al carrito (por si acaso)
    def get(self, request, product_id):
        return redirect('app_carts:cart')


# ---------------------------------------------------------------------------
# Remove (decrementa cantidad)
# ---------------------------------------------------------------------------

class RemoveCartView(View):
    def get(self, request, product_id, cart_item_id):
        services.remove_cart_item_quantity(request, product_id, cart_item_id)
        return redirect('app_carts:cart')


# ---------------------------------------------------------------------------
# Remove item (elimina completo)
# ---------------------------------------------------------------------------

class RemoveCartItemView(View):
    def get(self, request, product_id, cart_item_id):
        services.delete_cart_item(request, product_id, cart_item_id)
        return redirect('app_carts:cart')


# ---------------------------------------------------------------------------
# Cart
# ---------------------------------------------------------------------------

class CartView(TemplateView):
    template_name = 'carts/cart.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(services.get_cart_totals(self.request))
        return ctx


# ---------------------------------------------------------------------------
# Checkout
# ---------------------------------------------------------------------------

class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'carts/checkout.html'
    login_url     = 'app_users:login'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(services.get_cart_totals(self.request))
        return ctx
