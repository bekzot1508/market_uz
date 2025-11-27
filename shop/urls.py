from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # product
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),

    # review
    path('review/edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),

    # cart
    path('cart/', views.cart_view, name='cart_view'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),


    path('orders/', views.my_orders, name='my_orders'),
    path('checkout/address/', views.checkout_address, name='checkout_address'),
    path('checkout/confirm/', views.checkout_confirm, name='checkout_confirm'),
    path('checkout/success/<int:order_id>/', views.checkout_success, name='checkout_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    # path('my-orders/<int:order_id>/', views.order_detail, name='order_detail'),


]
