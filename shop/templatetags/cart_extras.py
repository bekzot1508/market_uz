# shop/templatetags/cart_extras.py
from django import template

register = template.Library()

@register.filter
def get_item(cart, product_id):
    """
    cart — odatda request.session['cart'] ko'rinishidagi dict
    product_id — product.id yoki string bo'lishi mumkin
    Returns quantity (int) yoki 0 agar mavjud bo'lmasa.
    """
    if not cart:
        return 0
    # Sessiyadagi kalitlar string bo'lishi mumkin, shuning uchun ikkala formatni tekshiramiz
    try:
        return cart.get(str(product_id), cart.get(int(product_id), 0))
    except Exception:
        # xavfsizlik uchun 0 qaytaramiz
        return 0


@register.filter
def cart_total_qty(cart):
    if not cart:
        return 0
    try:
        return sum(int(v) for v in cart.values())
    except Exception:
        return 0
