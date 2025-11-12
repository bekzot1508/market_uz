from django.shortcuts import render
from shop.models import Product, Order

# Create your views here.
def dashboard_home(request):
    return render(request, 'admin_dashboard/home.html')

def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin_dashboard/orders.html', {'orders': orders})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'admin_dashboard/products.html', {'products': products})
