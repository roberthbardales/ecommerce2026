"""
Store services — lógica de negocio desacoplada de las vistas.
"""
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Product, ReviewRating, ProductGallery
from .forms import ReviewForm


# ---------------------------------------------------------------------------
# Productos
# ---------------------------------------------------------------------------

def get_available_products(category=None, page=None, per_page=6):
    """
    Retorna un objeto Page de productos disponibles.
    Si se pasa category (instancia de Category), filtra por ella.
    """
    if category is not None:
        qs = Product.objects.filter(category=category, is_available=True)
    else:
        qs = Product.objects.filter(is_available=True).order_by('id')

    paginator = Paginator(qs, per_page)
    return paginator.get_page(page), qs.count()


def get_product_by_slugs(category_slug, product_slug):
    """
    Retorna el producto que coincida con ambos slugs o None.
    """
    try:
        return Product.objects.get(
            category__slug=category_slug,
            slug=product_slug,
        )
    except Product.DoesNotExist:
        return None


def search_products(keyword):
    """
    Busca productos por nombre o descripción.
    Retorna (queryset, count).
    """
    if not keyword:
        qs = Product.objects.none()
    else:
        qs = Product.objects.filter(
            Q(product_name__icontains=keyword) |
            Q(description__icontains=keyword)
        ).order_by('-created_date')
    return qs, qs.count()


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------

def get_reviews_for_product(product):
    """Retorna reviews activas de un producto."""
    return ReviewRating.objects.filter(product=product, status=True)


def submit_or_update_review(request, product_id):
    """
    Crea o actualiza una review para el producto dado.
    Retorna (success: bool, message: str).
    """
    try:
        existing = ReviewRating.objects.get(
            user__id=request.user.id,
            product__id=product_id,
        )
        form = ReviewForm(request.POST, instance=existing)
        if form.is_valid():
            form.save()
            return True, 'Thank you! Your review has been updated.'
        return False, 'Invalid form data.'
    except ReviewRating.DoesNotExist:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.ip         = request.META.get('REMOTE_ADDR', '')
            review.product_id = product_id
            review.user_id    = request.user.id
            review.save()
            return True, 'Thank you! Your review has been submitted.'
        return False, 'Invalid form data.'


# ---------------------------------------------------------------------------
# Galería
# ---------------------------------------------------------------------------

def get_product_gallery(product):
    """Retorna las imágenes de galería de un producto."""
    return ProductGallery.objects.filter(product=product)
