"""
Store views — CBV con capa de servicios.

Dependencias pendientes (comentadas hasta implementar):
  - carts: CartItem, _cart_id
  - orders: OrderProduct
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View

from applications.category.models import Category

from . import services


# ---------------------------------------------------------------------------
# Store / listado de productos
# ---------------------------------------------------------------------------

class StoreView(ListView):
    template_name = 'store/store.html'
    context_object_name = 'products'

    def get_queryset(self):
        # guardamos la categoría para reusar en get_context_data
        self._category = None
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            self._category = get_object_or_404(Category, slug=category_slug)
        page = self.request.GET.get('page')
        self._paged, self._count = services.get_available_products(
            category=self._category,
            page=page,
        )
        return self._paged

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['product_count'] = self._count
        return ctx


# ---------------------------------------------------------------------------
# Detalle de producto
# ---------------------------------------------------------------------------

class ProductDetailView(DetailView):
    template_name       = 'store/product_detail.html'
    context_object_name = 'single_product'

    def get_object(self):
        return get_object_or_404(
            __import__('applications.store.models', fromlist=['Product']).Product,
            category__slug=self.kwargs['category_slug'],
            slug=self.kwargs['product_slug'],
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product = self.get_object()

        # --- carts (pendiente) ---
        # from applications.carts.models import CartItem
        # from applications.carts.views import _cart_id
        # ctx['in_cart'] = CartItem.objects.filter(
        #     cart__cart_id=_cart_id(self.request), product=product
        # ).exists()
        ctx['in_cart'] = False

        # --- orders (pendiente) ---
        # if self.request.user.is_authenticated:
        #     from applications.orders.models import OrderProduct
        #     ctx['orderproduct'] = OrderProduct.objects.filter(
        #         user=self.request.user, product_id=product.id
        #     ).exists()
        # else:
        #     ctx['orderproduct'] = None
        ctx['orderproduct'] = None

        ctx['reviews']         = services.get_reviews_for_product(product)
        ctx['product_gallery'] = services.get_product_gallery(product)
        return ctx


# ---------------------------------------------------------------------------
# Búsqueda
# ---------------------------------------------------------------------------

class SearchView(ListView):
    template_name       = 'store/store.html'
    context_object_name = 'products'

    def get_queryset(self):
        keyword = self.request.GET.get('keyword', '').strip()
        self._qs, self._count = services.search_products(keyword)
        return self._qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['product_count'] = self._count
        return ctx


# ---------------------------------------------------------------------------
# Submit review
# ---------------------------------------------------------------------------

class SubmitReviewView(LoginRequiredMixin, View):
    """Solo acepta POST. Redirige de vuelta al referer."""

    def post(self, request, product_id):
        url = request.META.get('HTTP_REFERER', '/')
        success, msg = services.submit_or_update_review(request, product_id)
        if success:
            messages.success(request, msg)
        else:
            messages.error(request, msg)
        return redirect(url)
