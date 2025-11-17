from django import forms
from shop.models import Product, ProductImage
import json


# ================= ProductForm =================
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "discount_price",
            "stock",
            "category",
            "image",         # Main image
            "is_active",
            "extra_data",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "extra_data": forms.Textarea(attrs={"rows": 4}),
        }




# ================= ProductImageForm =================
class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ["image"]
