"""
Carts services — lógica de negocio desacoplada de las vistas.
"""
from django.core.exceptions import ObjectDoesNotExist

from applications.store.models import Product, Variation
from .models import Cart, CartItem


# ---------------------------------------------------------------------------
# Helpers de sesión
# ---------------------------------------------------------------------------

def get_cart_id(request):
    """Retorna el session_key, creando la sesión si no existe."""
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def get_or_create_cart(request):
    """Retorna el Cart asociado a la sesión actual, creándolo si no existe."""
    cart_id = get_cart_id(request)
    cart, _ = Cart.objects.get_or_create(cart_id=cart_id)
    return cart


# ---------------------------------------------------------------------------
# Variaciones
# ---------------------------------------------------------------------------

def get_product_variations(request, product):
    """
    Extrae las variaciones seleccionadas del POST y las devuelve
    como lista de instancias Variation.
    """
    product_variation = []
    if request.method == 'POST':
        for key, value in request.POST.items():
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value,
                )
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass
    return product_variation


# ---------------------------------------------------------------------------
# Add to cart
# ---------------------------------------------------------------------------

def add_item_to_cart(request, product_id):
    """
    Agrega un producto al carrito (usuario autenticado o anónimo).
    Si ya existe un CartItem con las mismas variaciones, incrementa quantity.
    De lo contrario crea uno nuevo.
    """
    product = Product.objects.get(id=product_id)
    product_variation = get_product_variations(request, product)

    if request.user.is_authenticated:
        _add_for_user(request.user, product, product_variation)
    else:
        cart = get_or_create_cart(request)
        _add_for_guest(cart, product, product_variation)


def _add_for_user(user, product, product_variation):
    cart_items = CartItem.objects.filter(product=product, user=user)

    if cart_items.exists():
        ex_var_list, ids = _get_existing_variations(cart_items)
        if product_variation in ex_var_list:
            idx     = ex_var_list.index(product_variation)
            item    = CartItem.objects.get(product=product, id=ids[idx])
            item.quantity += 1
            item.save()
        else:
            item = CartItem.objects.create(product=product, quantity=1, user=user)
            _set_variations(item, product_variation)
    else:
        item = CartItem.objects.create(product=product, quantity=1, user=user)
        _set_variations(item, product_variation)


def _add_for_guest(cart, product, product_variation):
    cart_items = CartItem.objects.filter(product=product, cart=cart)

    if cart_items.exists():
        ex_var_list, ids = _get_existing_variations(cart_items)
        if product_variation in ex_var_list:
            idx     = ex_var_list.index(product_variation)
            item    = CartItem.objects.get(product=product, id=ids[idx])
            item.quantity += 1
            item.save()
        else:
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            _set_variations(item, product_variation)
    else:
        item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        _set_variations(item, product_variation)


def _get_existing_variations(cart_items):
    ex_var_list = []
    ids = []
    for item in cart_items:
        ex_var_list.append(list(item.variations.all()))
        ids.append(item.id)
    return ex_var_list, ids


def _set_variations(item, variations):
    if variations:
        item.variations.clear()
        item.variations.add(*variations)
    item.save()


# ---------------------------------------------------------------------------
# Remove / delete
# ---------------------------------------------------------------------------

def remove_cart_item_quantity(request, product_id, cart_item_id):
    """Reduce en 1 la cantidad del CartItem. Si llega a 0, lo elimina."""
    product = Product.objects.get(id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(
                product=product, user=request.user, id=cart_item_id
            )
        else:
            cart      = get_or_create_cart(request)
            cart_item = CartItem.objects.get(
                product=product, cart=cart, id=cart_item_id
            )
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except CartItem.DoesNotExist:
        pass


def delete_cart_item(request, product_id, cart_item_id):
    """Elimina completamente un CartItem del carrito."""
    product = Product.objects.get(id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(
            product=product, user=request.user, id=cart_item_id
        )
    else:
        cart      = get_or_create_cart(request)
        cart_item = CartItem.objects.get(
            product=product, cart=cart, id=cart_item_id
        )
    cart_item.delete()


# ---------------------------------------------------------------------------
# Totales del carrito
# ---------------------------------------------------------------------------

def get_cart_totals(request):
    """
    Retorna dict con: cart_items, total, quantity, tax, grand_total.
    """
    total      = 0
    quantity   = 0
    tax        = 0
    grand_total = 0
    cart_items = None

    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart       = Cart.objects.get(cart_id=get_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for item in cart_items:
            total    += item.product.price * item.quantity
            quantity += item.quantity

        tax         = round((2 * total) / 100, 2)
        grand_total = round(total + tax, 2)

    except ObjectDoesNotExist:
        pass

    return {
        'cart_items':  cart_items,
        'total':       total,
        'quantity':    quantity,
        'tax':         tax,
        'grand_total': grand_total,
    }
