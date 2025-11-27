from django import forms
from .models import Product
from phonenumber_field.formfields import PhoneNumberField

class CheckoutAddressForm(forms.Form):
    full_name = forms.CharField(label="To‘liq ism", max_length=100)
    phone = PhoneNumberField(region='UZ', label="Telefon raqam")
    address = forms.CharField(label="Manzil: viloyat, tuman, qishloq, ko'cha, uy", widget=forms.Textarea)
    note = forms.CharField(label="Izoh (ixtiyoriy)", widget=forms.Textarea, required=False)



