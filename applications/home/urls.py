from django.urls import path
from . import views

app_name = "app_home"

urlpatterns = [
    # Auth
    path("register/", views.RegisterView.as_view(), name="register"),

]