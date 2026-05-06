from django.views.generic import ListView

from applications.store.models import Product

class HomeView(ListView):
    model = Product
    template_name = 'home.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(is_available=True).order_by('-created_date')[:8]
