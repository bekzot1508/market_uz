from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from shop.models import Product, Category, Order, OrderItemSnapshot, ProductImage
from user.models import CustomUser
from .forms import ProductForm, ProductImageForm, CategoryForm
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.utils.text import slugify
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
    return render(request, 'admin_dashboard/products_list.html', {'products': products})



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
def users_list(request):
    users = CustomUser.objects.all().order_by('-date_joined')
    return render(request, "admin_dashboard/users_list.html", {"users": users})
