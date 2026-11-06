from django.urls import path

from . import views

app_name = "purchases"

urlpatterns = [
    path("start/", views.purchase_start_view, name="start"),
    path("success/", views.purchase_success_view, name="success"),
    path("stopped/", views.purchase_stopped_view, name="stopped"),
    # path("buy/<int:product_id>/", views.purchase_buy_view, name="buy"),
]