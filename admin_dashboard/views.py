from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from shop.models import Product, Category, Order
from shop.forms import ProductForm
from user.models import CustomUser

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


# ================= Products CRUD =================
@login_required
@user_passes_test(staff_required)
def products_list(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'admin_dashboard/products_list.html', {'products': products})


# ================= Product Create =================
@login_required
@user_passes_test(staff_required)
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product created!")
            return redirect('admin_dashboard:products_list')
    else:
        form = ProductForm()
    return render(request, 'admin_dashboard/product_form.html', {'form': form})


# ================= Product Edit =================
@login_required
@user_passes_test(staff_required)
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated!")
            return redirect('admin_dashboard:products_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'admin_dashboard/product_form.html', {'form': form, 'product': product})


# ================= Product delete =================
@login_required
@user_passes_test(staff_required)
def product_delete(request, product_id):
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
