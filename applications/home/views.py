from django.views.generic import ListView

from applications.store.models import Product

class HomeView(ListView):
    model = Product
    template_name = 'home.html'
    context_object_name = 'products'