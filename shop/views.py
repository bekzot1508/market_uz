from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Product, Category, Order
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST


# Create your views here.
def home(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category')

    products = Product.objects.filter(is_active=True)
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(extra_data__icontains=query)
        )
    if category_id:
        products = products.filter(category_id=category_id)

    products = products.order_by('-average_rating', '-review_count', '-created_at')
    categories = Category.objects.filter(parent__isnull=True)

    return render(request, 'home.html', {
        'products': products,
        'categories': categories,
        'query': query
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'shop/product_detail.html', {'product': product})


# 🛒 CART
def cart_view(request):
    cart = request.session.get('cart', {})
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)

    total = sum(float(p.get_discounted_price()) * cart[str(p.id)] for p in products)

    return render(request, 'shop/cart.html', {
        'products': products,
        'cart': cart,
        'total': total
    })

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    return redirect('shop:cart_view')

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('shop:cart_view')




@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return render(request, 'shop/checkout.html', {'error': 'Savat bo‘sh!'})

    products = Product.objects.filter(id__in=cart.keys())

    total = 0
    for product in products:
        quantity = cart.get(str(product.id), 0)
        total += product.get_discounted_price() * quantity

    # Buyurtma yaratamiz
    order = Order.objects.create(
        user=request.user,
        items=cart,
        total_price=total
    )

    # Savatni tozalaymiz
    request.session['cart'] = {}

    return render(request, 'shop/checkout_success.html', {'order': order})




#############  Admin Dashboard  #############
@staff_member_required
def admin_dashboard(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    orders = Order.objects.all().order_by('-created_at')

    # Filtrlash
    if query:
        orders = orders.filter(
            Q(user__username__icontains=query) |
            Q(id__icontains=query)
        )
    if status_filter:
        orders = orders.filter(status=status_filter)

    context = {
        'orders': orders,
        'query': query,
        'status_filter': status_filter,
    }
    return render(request, 'shop/admin_dashboard.html', context)

@staff_member_required
@require_POST
def update_order_status(request, order_id):
    order = Order.objects.get(id=order_id)
    new_status = request.POST.get('status')
    if new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        order.save()
    return redirect('shop:admin_dashboard')




#############  My Orders  #############
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/my_orders.html', {'orders': orders})

@login_required
def checkout_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/checkout_success.html', {'order': order})




