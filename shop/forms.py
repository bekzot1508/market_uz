from django import forms
from .models import Product

class CheckoutAddressForm(forms.Form):
    full_name = forms.CharField(label="To‘liq ism", max_length=100)
    phone = forms.CharField(label="Telefon raqam", max_length=20)
    address = forms.CharField(label="Manzil", widget=forms.Textarea)
    note = forms.CharField(label="Izoh (ixtiyoriy)", widget=forms.Textarea, required=False)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'image', 'category', 'description', 'price', 'discount_price', 'stock', 'is_active']
