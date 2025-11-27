from django import template
from django.urls import reverse
from shop.models import Product

register = template.Library()

@register.filter
def get_product(product_id):
    try:
        return Product.objects.get(id=int(product_id))
    except (Product.DoesNotExist, ValueError, TypeError):
        return None


@register.filter
def to_int(value):
    """Template ichida string -> int ga o‘tkazish uchun"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

@register.simple_tag
def product_detail_url(product_id):
    """Mahsulot detail sahifasiga URL qaytaradi"""
    try:
        product = Product.objects.get(id=product_id)
        return reverse('shop:product_detail', args=[product.id])
    except Product.DoesNotExist:
        return '#'



@register.filter
def get_deleted_product_name(product_id):
    # Oxirgi ma’lumotni qaytarish yoki IDni chiqarish
    return f"Product #{product_id}"




from django import template
register = template.Library()

@register.filter
def times(number):
    """
    Template ichida range() o‘rniga ishlatamiz.
    {% for i in 5|times %}
    """
    return range(int(number))



