from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from shop.models import Product, Category, Order, OrderItemSnapshot, ProductImage, ProductReview
from user.models import CustomUser
from .forms import ProductForm, ProductImageForm, CategoryForm, CustomUserForm
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.utils.text import slugify
from django.core.paginator import Paginator
from datetime import datetime
import json


# Create your views here.
# ================= Staff required =================
def staff_required(user):
    return user.is_staff

# ================= Home =================
@login_required
@user_passes_test(staff_required)
def dashboard_home(request):
    context = {
        'product_count': Product.objects.count(),
        'order_count': Order.objects.count(),
        'category_count': Category.objects.count(),
        'user_count': CustomUser.objects.count(),
    }
    return render(request, 'admin_dashboard/dashboard_home.html', context)


#===============================
#   ADMIN PRODUCT MANAGE
#===============================
# ================= Products LIST =================
@login_required
@user_passes_test(staff_required)


def admin_products_list(request):
    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all()

    # Filters
    category = request.GET.get('category')
    is_active = request.GET.get('is_active')
    stock = request.GET.get('stock')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    search = request.GET.get('search')

    if category:
        products = products.filter(category_id=category)
    if is_active in ['0', '1']:
        products = products.filter(is_active=bool(int(is_active)))
    if stock == '0':
        products = products.filter(stock=0)
    elif stock == '1':
        products = products.filter(stock__gt=0)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if search:
        products = products.filter(name__icontains=search)

    # Pagination
    paginator = Paginator(products, 15)  # 10 ta product per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_dashboard/products_list.html', {
        'products': page_obj,
        'categories': categories
    })




@staff_member_required
def admin_product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            if not product.slug:
                product.slug = slugify(product.name)

            # ✅ Extra Data JSON parse
            extra_raw = request.POST.get("extra_data") or "{}"
            try:
                extra_parsed = json.loads(extra_raw)
            except json.JSONDecodeError:
                messages.error(request, "Extra Data must be valid JSON!")
                return redirect("admin_dashboard:product_create")
            product.extra_data = extra_parsed
            product.save()

            # ✅ Save multiple images
            images = request.FILES.getlist("images")
            for img in images:
                ProductImage.objects.create(product=product, image=img)

            messages.success(request, "Product created successfully!")
            return redirect("admin_dashboard:products_list")
    else:
        form = ProductForm()

    return render(request, "admin_dashboard/product_form.html", {"form": form, "product": None})


@staff_member_required
def admin_product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            if not product.slug:
                product.slug = slugify(product.name)

            # ✅ Extra Data JSON parse
            extra_raw = request.POST.get("extra_data") or "{}"
            try:
                extra_parsed = json.loads(extra_raw)
            except json.JSONDecodeError:
                messages.error(request, "Extra Data must be valid JSON!")
                return redirect("admin_dashboard:product_edit", product_id=product.id)
            product.extra_data = extra_parsed
            product.save()

            # ✅ Delete selected images
            delete_ids = request.POST.getlist("delete_images")
            if delete_ids:
                ProductImage.objects.filter(id__in=delete_ids, product=product).delete()

            # ✅ Save new images
            images = request.FILES.getlist("images")
            for img in images:
                ProductImage.objects.create(product=product, image=img)

            messages.success(request, "Product updated successfully!")
            return redirect("admin_dashboard:products_list")
    else:
        form = ProductForm(instance=product)

    return render(request, "admin_dashboard/product_form.html", {"form": form, "product": product})


# ================= Product delete =================
@login_required
@user_passes_test(staff_required)
def admin_product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted!")
        return redirect('admin_dashboard:products_list')
    return render(request, 'admin_dashboard/product_delete.html', {'product': product})







# def dashboard_home(request):
#     return render(request, 'admin_dashboard/home.html')
#
# def order_list(request):
#     orders = Order.objects.all().order_by('-created_at')
#     return render(request, 'admin_dashboard/orders.html', {'orders': orders})
#
# def product_list(request):
#     products = Product.objects.all()
#     return render(request, 'admin_dashboard/products.html', {'products': products})


#===============================
#   ADMIN OREDERS MANAGE
#===============================
# ================= admin_orders_list =================
@staff_member_required
def admin_orders_list(request):
    """Admin dashboard: orders list with search & status filter"""
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

    context = {
        "orders": orders,
        "query": query,
        "status_filter": status_filter
    }
    return render(request, "admin_dashboard/orders_list.html", context)


@staff_member_required
@require_POST
def admin_update_order_status(request, order_id):
    """Update order status from admin panel"""
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')

    if new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        order.save()

    return redirect("admin_dashboard:orders_list")


@staff_member_required
def admin_order_detail(request, order_id):
    """Order detail page for admin with snapshots"""
    order = get_object_or_404(Order, id=order_id)
    snapshots = order.snapshots.all()

    return render(request, "admin_dashboard/order_detail.html", {
        "order": order,
        "snapshots": snapshots
    })



#===============================
#   ADMIN CATEGORIES MANAGE
#===============================
@staff_member_required
def categories_list(request):
    categories = Category.objects.filter(parent__isnull=True)
    return render(request, "admin_dashboard/category_list.html", {"categories": categories})


@staff_member_required
@staff_member_required
def category_create(request):
    parent_id = request.GET.get("parent")
    initial = {}
    if parent_id:
        try:
            initial["parent"] = Category.objects.get(id=int(parent_id))
        except (Category.DoesNotExist, ValueError):
            pass

    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Kategoriya yaratildi.")
            return redirect("admin_dashboard:categories_list")
    else:
        form = CategoryForm(initial=initial)

    return render(request, "admin_dashboard/category_form.html", {
        "title": "Create Category",
        "form": form
    })



@staff_member_required
@staff_member_required
def category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Kategoriya yangilandi.")
            return redirect("admin_dashboard:categories_list")
    else:
        form = CategoryForm(instance=category)

    return render(request, "admin_dashboard/category_form.html", {
        "title": "Edit Category",
        "form": form
    })




@staff_member_required
def category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        category.delete()
        return redirect("admin_dashboard:categories_list")

    return render(request, "admin_dashboard/category_delete_confirm.html", {"category": category})



#===============================
#   ADMIN CATEGORIES MANAGE
#===============================
from django.shortcuts import render
from django.db.models import Q
from user.models import CustomUser

def users_list(request):
    users = CustomUser.objects.all().order_by('-date_joined')

    # SEARCH
    query = request.GET.get('search', '')
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone_number__icontains=query)
        )

    # ROLE FILTER
    role = request.GET.get('role', '')
    if role == 'admin':
        users = users.filter(is_superuser=True)
    elif role == 'user':
        users = users.filter(is_superuser=False)

    # STATUS FILTER
    status = request.GET.get('status', '')
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)

    context = {
        'users': users,
        'request': request,  # needed to keep form values
    }
    return render(request, "admin_dashboard/users_list.html", context)



def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == "POST":
        form = CustomUserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully!")
            return redirect('admin_dashboard:users_list')
    else:
        form = CustomUserForm(instance=user)
    return render(request, 'admin_dashboard/edit_user.html', {'form': form, 'user': user})


def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        user.delete()
        messages.success(request, "User deleted successfully!")
        return redirect('admin_dashboard:users_list')

    # GET so‘rov bo‘lsa, tasdiqlash sahifasini ko‘rsatamiz
    return render(request, 'admin_dashboard/delete_user.html', {'user': user})


def view_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, 'admin_dashboard/view_user.html', {'user': user})



#===============================
#   ADMIN CATEGORIES MANAGE
#===============================
# def reviews_list(request):
#     reviews = ProductReview.objects.select_related("user", "product").order_by("-created_at")
#     return render(request, "admin_dashboard/reviews_list.html", {"reviews": reviews})



def reviews_list(request):
    reviews = ProductReview.objects.all().order_by('-created_at')

    product = request.GET.get('product')
    user = request.GET.get('user')
    stars = request.GET.get('stars')
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')
    search = request.GET.get('search')

    if product:
        reviews = reviews.filter(product_id=product)

    if user:
        reviews = reviews.filter(user_id=user)

    if stars:
        reviews = reviews.filter(stars_given=stars)

    if date_from:
        reviews = reviews.filter(created_at__gte=date_from)

    if date_to:
        date_to_full = datetime.strptime(date_to, "%Y-%m-%d")
        date_to_full = date_to_full.replace(hour=23, minute=59)
        reviews = reviews.filter(created_at__lte=date_to_full)

    if search:
        reviews = reviews.filter(comment__icontains=search)

    paginator = Paginator(reviews, 5)  # 5 review per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "reviews": page_obj,
        "products": Product.objects.all(),
        "users": CustomUser.objects.all(),
        "request_get": request.GET.copy(),  # pagination linklar uchun
    }

    return render(request, 'admin_dashboard/reviews_list.html', context)





def delete_review(request, review_id):
    review = get_object_or_404(ProductReview, id=review_id)

    if request.method == "POST":
        review.delete()
        messages.success(request, "Review deleted successfully!")
        return redirect("admin_dashboard:reviews_list")

    return render(request, "admin_dashboard/delete_review.html", {"review": review})
