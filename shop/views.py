from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q

from .forms import CheckoutAddressForm, ProductForm
from .models import Product, Category, Order, OrderItemSnapshot, ProductReview
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.contrib import messages



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
    reviews = product.reviews.all().order_by('-created_at')

    # POST review
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Review qoldirish uchun login qilishingiz kerak.")
            return redirect('user:login')

        comment = request.POST.get('comment')
        stars = request.POST.get('stars')

        if comment and stars:
            try:
                stars = int(stars)
            except ValueError:
                stars = 0
            if 1 <= stars <= 5:
                ProductReview.objects.create(
                    user=request.user,
                    product=product,
                    comment=comment,
                    stars_given=stars
                )
                messages.success(request, "Review muvaffaqiyatli qo‘shildi!")
            else:
                messages.error(request, "Iltimos, 1 dan 5 gacha rating kiriting!")
            return redirect('shop:product_detail', slug=product.slug)
        else:
            messages.error(request, "Iltimos, comment va ratingni to‘ldiring.")

    # extra_datani parse qilamiz (string bo‘lsa)
    if isinstance(product.extra_data, dict):
        extra_data = product.extra_data
    else:
        import json
        try:
            extra_data = json.loads(product.extra_data)
        except Exception:
            extra_data = {}

    context = {
        'product': product,
        'reviews': reviews,
        'extra_data': extra_data
    }
    return render(request, 'shop/product_detail.html', context)



@login_required
def edit_review(request, review_id):
    review = get_object_or_404(ProductReview, id=review_id, user=request.user)
    product = review.product

    if request.method == "POST":
        comment = request.POST.get('comment')
        stars = request.POST.get('stars')

        if not comment or not stars:
            messages.error(request, "Iltimos, comment va ratingni to‘ldiring.")
        else:
            review.comment = comment
            review.stars_given = int(stars)
            review.save()
            messages.success(request, "Review muvaffaqiyatli yangilandi!")
            return redirect('shop:product_detail', slug=product.slug)

    context = {
        'review': review,
        'product': product
    }
    return render(request, 'shop/edit_review.html', context)



# --------------------------
# Review delete
@login_required
def delete_review(request, review_id):
    review = get_object_or_404(ProductReview, id=review_id, user=request.user)
    product_slug = review.product.slug
    review.delete()
    messages.success(request, "Review muvaffaqiyatli o‘chirildi!")
    return redirect('shop:product_detail', slug=product_slug)



@staff_member_required
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('shop:product_detail', slug=product.slug)
    else:
        form = ProductForm(instance=product)

    return render(request, 'shop/product_edit.html', {'form': form, 'product': product})


@staff_member_required
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product.delete()
        return redirect('home')

    return render(request, 'shop/product_delete.html', {'product': product})



#############  CART #############

def cart_view(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())

    total = sum(
        float(p.get_discounted_price()) * cart[str(p.id)]
        for p in products
    )

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



#############  CHECKOUT (2-step) #############

@login_required
def checkout_address(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('shop:cart_view')

    if request.method == "POST":
        form = CheckoutAddressForm(request.POST)
        if form.is_valid():
            request.session['checkout_address'] = form.cleaned_data
            return redirect('shop:checkout_confirm')
    else:
        form = CheckoutAddressForm()

    return render(request, 'shop/checkout_address.html', {"form": form})


@login_required
def checkout_confirm(request):
    cart = request.session.get('cart', {})
    address = request.session.get('checkout_address', {})

    if not cart or not address:
        return redirect('shop:checkout_address')

    products = Product.objects.filter(id__in=cart.keys())

    total = sum(
        p.get_discounted_price() * cart[str(p.id)]
        for p in products
    )

    if request.method == "POST":
        order = Order.objects.create(
            user=request.user,
            items=cart,
            total_price=total,
            full_name=address['full_name'],
            phone=address['phone'],
            address=address['address'],
            note=address.get('note', '')
        )

        # 📌 SNAPSHOT YARATAMIZ
        for p in products:
            snap = OrderItemSnapshot.objects.create(
                product_id=p.id,
                name=p.name,
                image=p.image.url if p.image else "no_image.jpg",
                price=p.get_discounted_price(),
                quantity=cart[str(p.id)]
            )
            order.snapshots.add(snap)

        # savatni tozalaymiz
        request.session['cart'] = {}
        request.session['checkout_address'] = {}

        return redirect('shop:checkout_success', order_id=order.id)

    return render(request, 'shop/checkout_confirm.html', {
        "products": products,
        "cart": cart,
        "address": address,
        "total": total,
    })



#############  ADMIN #############

@staff_member_required
def admin_dashboard(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    orders = Order.objects.all().order_by('-created_at')

    if query:
        orders = orders.filter(
            Q(user__username__icontains=query) |
            Q(id__icontains=query)
        )
    if status_filter:
        orders = orders.filter(status=status_filter)

    return render(request, 'shop/admin_dashboard.html', {
        'orders': orders,
        'query': query,
        'status_filter': status_filter,
    })


@staff_member_required
@require_POST
def update_order_status(request, order_id):
    order = Order.objects.get(id=order_id)
    new_status = request.POST.get('status')
    if new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        order.save()
    return redirect('shop:admin_dashboard')



#############  MY ORDERS #############

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/my_orders.html', {"orders": orders})


@login_required
def checkout_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    snapshots = order.snapshots.all()

    return render(request, 'shop/checkout_success.html', {
        "order": order,
        "snapshots": snapshots
    })


