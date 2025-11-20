from django import forms
from shop.models import Product, ProductImage, Category
import json

from user.models import CustomUser


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


# ================= CategoryForm =================
class CategoryForm(forms.ModelForm):
    parent = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="--- None ---"
    )

    class Meta:
        model = Category
        fields = ["name", "parent"]

    def clean_name(self):
        name = self.cleaned_data.get("name").strip()
        qs = Category.objects.filter(name__iexact=name)  # case-insensitive filter
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)  # editda o'zini chiqarib tashlash
        if qs.exists():
            raise forms.ValidationError("Bu nomdagi kategoriya allaqachon mavjud.")
        return name

    def clean_parent(self):
        parent = self.cleaned_data.get("parent")
        if parent and self.instance and parent.id == self.instance.id:
            raise forms.ValidationError("O'zingizni parent qilolmaysiz.")
        return parent




# ================= CustomUserForm =================
class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'profile_picture', 'is_active', 'is_superuser']
