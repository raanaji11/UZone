from dataclasses import field
from xml.dom import ValidationErr
from django import forms 
from store.models import User, Product, Coupon, Address

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('category', 'name', 'price', 'description', 'image')

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data['price']

        if price < 0:
            raise forms.ValidationError("Please enter a valid price.")

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ('category', 'code', 'desc', 'discount_percentage')

    def clean(self):
        cleaned_data = super().clean()
        discount_percentage = cleaned_data['discount_percentage']
        code = cleaned_data['code']

        if discount_percentage < 0:
            raise forms.ValidationError("Please enter a valid value.")

        if len(code) < 6:
            raise forms.ValidationError("Code length should be 6 character or longer.")


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('mobile', 'address', 'city', 'state', 'zip_code')

    def clean(self):
        cleaned_data = super().clean()
        mobile = cleaned_data['mobile']
        zip_code = cleaned_data['zip_code']

        if len(str(mobile)) < 10 or len(str(mobile)) > 10:
            raise forms.ValidationError("Mobile number be of 10 digits.")

        if len(str(zip_code)) != 6:
            raise forms.ValidationError("Please enter a valid zip code.")