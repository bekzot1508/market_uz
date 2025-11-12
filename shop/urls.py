from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart_view'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('checkout/', views.checkout, name='checkout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('update-order-status/<int:order_id>/', views.update_order_status, name='update_order_status'),


]
