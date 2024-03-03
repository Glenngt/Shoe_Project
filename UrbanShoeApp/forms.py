from django import forms
from django.contrib.auth.models import User
from . import models
from django.contrib.auth.forms import UserCreationForm


class CustomerUserForm(forms.ModelForm):
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('seller', 'Seller'),
    ]

    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, required=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password', 'user_type']
        widgets = {
            'password': forms.PasswordInput(),
            
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = models.Customer
        fields = ['address', 'mobile','user_type']  


class ProductForm(forms.ModelForm):
    class Meta:
        model=models.Product
        fields=['name','price','quantity','description','product_image']

#address of shipment
class AddressForm(forms.Form):
    Email = forms.EmailField()
    Mobile= forms.IntegerField()
    Address = forms.CharField(max_length=500)

class FeedbackForm(forms.ModelForm):
    class Meta:
        model=models.Feedback
        fields=['name','feedback']

#for updating status of order
class OrderForm(forms.ModelForm):
    class Meta:
        model = models.Orders
        fields = ['address', 'mobile', 'status']

    # Additional fields from CartProduct
    product = forms.ModelChoiceField(queryset=models.CartProduct.objects.all().values_list('product', flat=True).distinct(), required=False)
    rate = forms.IntegerField(required=False)
    quantity = forms.IntegerField(required=False)
    subtotal = forms.IntegerField(required=False)

    # Additional field from Cart
    total = forms.IntegerField(required=False)

class EditOrderForm(forms.ModelForm):
    class Meta:
        model = models.CartProduct
        fields = ['product','rate','quantity', 'subtotal']        
    
    def __init__(self, *args, **kwargs):
        super(EditOrderForm, self).__init__(*args, **kwargs)

        # Make 'product' and 'rate' fields read-only
        self.fields['product'].widget.attrs['readonly'] = True
        self.fields['rate'].widget.attrs['readonly'] = True

        # Disable the 'product' and 'rate' fields from being rendered as HTML input elements
        self.fields['product'].disabled = True
        self.fields['rate'].disabled = True

class SellerOrderForm(forms.ModelForm):
    class Meta:
        model = models.SellerOrders
        fields = ['address', 'mobile', 'status']

    # Additional fields from CartProduct
    product = forms.ModelChoiceField(queryset=models.SellerCartProduct.objects.all().values_list('product', flat=True).distinct(), required=False)
    rate = forms.IntegerField(required=False)
    quantity = forms.IntegerField(required=False)
    subtotal = forms.IntegerField(required=False)

    # Additional field from Cart
    total = forms.IntegerField(required=False)

class SellerEditOrderForm(forms.ModelForm):
   

    class Meta:
        model = models.CartProduct
        fields = ['product', 'rate', 'quantity', 'subtotal']

    def __init__(self, *args, **kwargs):
        super(SellerEditOrderForm, self).__init__(*args, **kwargs)

        # Make 'product' and 'rate' fields read-only
        self.fields['product'].widget.attrs['readonly'] = True
        self.fields['rate'].widget.attrs['readonly'] = True

        # Disable the 'product' and 'rate' fields from being rendered as HTML input elements
        self.fields['product'].disabled = True
        self.fields['rate'].disabled = True

#for contact us page
class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 5, 'cols': 30}))


class SellerAddressForm(forms.Form):
    Mobile= forms.IntegerField()
    PickupAddress = forms.CharField(max_length=500)



