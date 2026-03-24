from .models import Cart, CartItem
from .services import get_cart_id


def counter(request):
    """Inyecta cart_count en todos los templates."""
    if 'admin' in request.path:
        return {}

    cart_count = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
        else:
            cart       = Cart.objects.filter(cart_id=get_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart[:1])

        for item in cart_items:
            cart_count += item.quantity

    except Cart.DoesNotExist:
        pass

    return {'cart_count': cart_count}
