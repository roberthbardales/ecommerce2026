"""
Orders services — lógica de negocio desacoplada de las vistas.
"""
import datetime
import json

from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from applications.carts.models import CartItem
from applications.store.models import Product
from .models import Order, OrderProduct, Payment


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def generate_order_number(order_id):
    """Genera un número de orden con formato YYYYMMDD + id."""
    today = datetime.date.today()
    return today.strftime('%Y%m%d') + str(order_id)


def get_cart_totals_for_user(user):
    """
    Calcula total, quantity, tax y grand_total a partir del carrito del usuario.
    Retorna dict o None si el carrito está vacío.
    """
    cart_items = CartItem.objects.filter(user=user)
    if not cart_items.exists():
        return None

    total    = 0
    quantity = 0
    for item in cart_items:
        total    += item.product.price * item.quantity
        quantity += item.quantity

    tax         = round((2 * total) / 100, 2)
    grand_total = round(total + tax, 2)

    return {
        'cart_items':  cart_items,
        'total':       total,
        'quantity':    quantity,
        'tax':         tax,
        'grand_total': grand_total,
    }


# ---------------------------------------------------------------------------
# Place order
# ---------------------------------------------------------------------------

def create_order(user, form_data, totals):
    """
    Crea y persiste una Order a partir de los datos del form y los totales.
    Retorna la instancia de Order.
    """
    order = Order()
    order.user           = user
    order.first_name     = form_data['first_name']
    order.last_name      = form_data['last_name']
    order.phone          = form_data['phone']
    order.email          = form_data['email']
    order.address_line_1 = form_data['address_line_1']
    order.address_line_2 = form_data.get('address_line_2', '')
    order.country        = form_data['country']
    order.state          = form_data['state']
    order.city           = form_data['city']
    order.order_note     = form_data.get('order_note', '')
    order.order_total    = totals['grand_total']
    order.tax            = totals['tax']
    order.ip             = form_data.get('ip', '')
    order.save()

    order.order_number = generate_order_number(order.id)
    order.save()
    return order


# ---------------------------------------------------------------------------
# Process payment
# ---------------------------------------------------------------------------

def process_payment(request):
    """
    Procesa el pago (payload JSON), crea Payment y OrderProduct,
    reduce stock, limpia el carrito y envía email de confirmación.
    Retorna dict con order_number y transID.
    """
    body    = json.loads(request.body)
    order   = Order.objects.get(
        user=request.user,
        is_ordered=False,
        order_number=body['orderID'],
    )

    # Crear Payment
    payment = Payment.objects.create(
        user           = request.user,
        payment_id     = body['transID'],
        payment_method = body['payment_method'],
        amount_paid    = order.order_total,
        status         = body['status'],
    )

    order.payment   = payment
    order.is_ordered = True
    order.save()

    # Mover CartItems → OrderProduct
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        op = OrderProduct.objects.create(
            order         = order,
            payment       = payment,
            user          = request.user,
            product       = item.product,
            quantity      = item.quantity,
            product_price = item.product.price,
            ordered       = True,
        )
        op.variations.set(item.variations.all())
        op.save()

        # Reducir stock
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Limpiar carrito
    cart_items.delete()

    # Email de confirmación
    _send_order_confirmation_email(request.user, order)

    return {
        'order_number': order.order_number,
        'transID':      payment.payment_id,
    }


def _send_order_confirmation_email(user, order):
    subject = 'Thank you for your order!'
    message = render_to_string('orders/order_recieved_email.html', {
        'user':  user,
        'order': order,
    })
    email = EmailMessage(subject, message, to=[user.email])
    email.send()


# ---------------------------------------------------------------------------
# Order complete
# ---------------------------------------------------------------------------

def get_order_complete_context(order_number, trans_id):
    """
    Retorna el contexto para la vista order_complete.
    Lanza Order.DoesNotExist o Payment.DoesNotExist si no se encuentran.
    """
    order            = Order.objects.get(order_number=order_number, is_ordered=True)
    ordered_products = OrderProduct.objects.filter(order=order)
    payment          = Payment.objects.get(payment_id=trans_id)

    subtotal = sum(p.product_price * p.quantity for p in ordered_products)

    return {
        'order':            order,
        'ordered_products': ordered_products,
        'order_number':     order.order_number,
        'transID':          payment.payment_id,
        'payment':          payment,
        'subtotal':         subtotal,
    }
