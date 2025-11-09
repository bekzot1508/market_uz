from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Product, Category


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

    return render(request, 'shop/home.html', {
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
    return redirect('cart_view')


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('cart_view')
