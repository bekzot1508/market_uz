from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),

    # Products
    path('products/', views.products_list, name='products_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product_delete'),

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
