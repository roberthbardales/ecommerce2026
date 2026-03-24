
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    path('users/', include('applications.users.urls', namespace='app_users')),
    path('store/', include('applications.store.urls', namespace='app_store')),
    path('carts/', include('applications.carts.urls', namespace='app_carts')),
    path('orders/', include('applications.orders.urls', namespace='app_orders')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)