"""
Orders views — CBV con capa de servicios.
Pasarela: Culqi (tarjetas + Yape + Plin)
"""
from django.conf import settings as django_settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import View, TemplateView
from django.http import JsonResponse, HttpResponse


from .forms import OrderForm
from . import services


# ---------------------------------------------------------------------------
# Place Order
# ---------------------------------------------------------------------------

class PlaceOrderView(LoginRequiredMixin, View):
    login_url = 'app_users:login'

    def get(self, request):
        return HttpResponse(f'<pre>POST data:\n{request.POST}\n\nErrores del form:\n{form.errors}</pre>')

    def post(self, request):
        print('Usuario:', request.user, '| Autenticado:', request.user.is_authenticated)
        print('POST:', request.POST)
        totals = services.get_cart_totals_for_user(request.user)
        if not totals:
            return redirect('app_store:store')

        form = OrderForm(request.POST)
        print('Form válido:', form.is_valid())
        print('Errores:', form.errors)
        if form.is_valid():
            form_data       = form.cleaned_data
            form_data['ip'] = request.META.get('REMOTE_ADDR', '')
            order           = services.create_order(request.user, form_data, totals)

            context = {
                'order':                order,
                'cart_items':           totals['cart_items'],
                'total':                totals['total'],
                'tax':                  totals['tax'],
                'grand_total':          totals['grand_total'],
                # Culqi requiere monto en centavos y la llave pública
                'grand_total_centavos': int(round(totals['grand_total'] * 100)),
                'culqi_public_key':     django_settings.CULQI_PUBLIC_KEY,
            }
            return render(request, 'orders/payments.html', context)

        return redirect('app_carts:checkout')


# ---------------------------------------------------------------------------
# Payments — Culqi (AJAX)
# ---------------------------------------------------------------------------

class PaymentsView(LoginRequiredMixin, View):
    login_url = 'app_users:login'

    def post(self, request):
        try:
            data = services.process_culqi_payment(request)
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


# ---------------------------------------------------------------------------
# Order Complete
# ---------------------------------------------------------------------------

class OrderCompleteView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/order_complete.html'
    login_url     = 'app_users:login'

    def get(self, request, *args, **kwargs):
        order_number = request.GET.get('order_number')
        trans_id     = request.GET.get('payment_id')

        try:
            context = services.get_order_complete_context(order_number, trans_id)
        except Exception:
            return redirect('app_store:store')

        return self.render_to_response(context)