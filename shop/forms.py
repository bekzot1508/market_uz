from django import forms

class CheckoutAddressForm(forms.Form):
    full_name = forms.CharField(label="To‘liq ism", max_length=100)
    phone = forms.CharField(label="Telefon raqam", max_length=20)
    address = forms.CharField(label="Manzil", widget=forms.Textarea)
    note = forms.CharField(label="Izoh (ixtiyoriy)", widget=forms.Textarea, required=False)
