from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),

    # Products
    path('products/', views.admin_products_list, name='products_list'),
    path('products/create/', views.admin_product_create, name='product_create'),
    path('products/<int:product_id>/edit/', views.admin_product_edit, name='product_edit'),
    path('products/<int:product_id>/delete/', views.admin_product_delete, name='product_delete'),

    path("orders/", views.admin_orders_list, name="orders_list"),
    path("orders/<int:order_id>/", views.admin_order_detail, name="order_detail"),
    path("orders/<int:order_id>/update-status/", views.admin_update_order_status, name="update_order_status"),

    # path("orders", views.orders_list, name="orders_list"),
    # path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
    # path("orders/<int:order_id>/delete/", views.order_delete, name="order_delete"),
    # path("orders/<int:order_id>/status/", views.order_update_status, name="order_update_status"),

    # # Orders
    # path('orders/', views.orders_list, name='orders_list'),
    #
    # # Categories
    # path('categories/', views.categories_list, name='categories_list'),
    #
    # # Users
    # path('users/', views.users_list, name='users_list'),
    #
    # # Reviews Moderation
    # path('reviews/', views.reviews_list, name='reviews_list'),

]
