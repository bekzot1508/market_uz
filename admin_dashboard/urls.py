from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('orders/', views.order_list, name='orders'),
    path('products/', views.product_list, name='products'),
]
