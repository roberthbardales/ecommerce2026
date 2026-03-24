from django.urls import path

from . import views

app_name = 'app_carts'

urlpatterns = [
    path('', views.CartView.as_view(), name='cart'),
    path('add/<int:product_id>/',
         views.AddCartView.as_view(), name='add_cart'),
    path('remove/<int:product_id>/<int:cart_item_id>/',
         views.RemoveCartView.as_view(), name='remove_cart'),
    path('remove-item/<int:product_id>/<int:cart_item_id>/',
         views.RemoveCartItemView.as_view(), name='remove_cart_item'),
    path('checkout/',
         views.CheckoutView.as_view(), name='checkout'),
]
