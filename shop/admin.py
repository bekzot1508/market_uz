from django.contrib import admin
from django import forms
from .models import Product, Category, Order, ProductImage

# Inline for product images
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", )


# Custom JSON widget for extra_data
class JSONTextArea(forms.Textarea):
    class Media:
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.5/codemirror.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.5/mode/javascript/javascript.min.js',
        )
        css = {'all': ('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.5/codemirror.min.css',)}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({'rows': 15, 'cols': 80, 'style': 'font-family: monospace; background: #f9f9f9;'})


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'extra_data': JSONTextArea(),
        }


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('name', 'category', 'price', 'stock', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    inlines = [ProductImageInline]

    class Media:
        js = ('shop/admin/js/json_editor.js',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_title', 'user', 'full_name', 'phone', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__username', 'full_name', 'phone', 'address')

    def order_title(self, obj):
        items = []
        for product_id, qty in obj.items.items():
            try:
                product = Product.objects.get(id=product_id)
                items.append(f"{product.name} (x{qty})")
            except Product.DoesNotExist:
                items.append(f"Unknown product (ID: {product_id})")
        return f"Order #{obj.id} — {obj.user.username} — {', '.join(items)}"

    order_title.short_description = "Order"
