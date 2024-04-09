from django.db import models
from django.db.models import Count, Sum
from django.contrib.auth.models import User
# Create your models here.
class Customer(models.Model):
    USER_TYPE_CHOICES = [
         ('customer', 'Customer'),
        ('seller', 'Seller'),
    ]
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/CustomerProfilePic/',null=True,blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=False)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return self.user.first_name
    def get_sellercart_total_earning(self):
        return self.sellercart_set.aggregate(total_earning=Sum('sellerorders__cart__cartproduct__subtotal'))['total_earning'] or 0
    

class Product(models.Model):
    name=models.CharField(max_length=40)
    product_image= models.ImageField(upload_to='product_image/',null=True,blank=True)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=20)
    description=models.CharField(max_length=40)
    def __str__(self):
        return self.name
    
    def update_product_quantities(self):
        # Update product quantities based on the items in the cart
        cart_products = CartProduct.objects.filter(cart=self.cart)
        for cart_product in cart_products:
            product = cart_product.product
            product.quantity -= cart_product.quantity
            product.save()





class Feedback(models.Model):
    name=models.CharField(max_length=40)
    feedback=models.CharField(max_length=500)
    date= models.DateField(auto_now_add=True,null=True)
    def __str__(self):
        return self.name



class cart(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.PositiveIntegerField(default=0)



class CartProduct(models.Model):
    cart = models.ForeignKey(cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rate = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return "cart:" + str(self.cart.id) + "cartproduct:" + str(self.id)
    

class Orders(models.Model):
    STATUS =(
        ('Pending','Pending'),
        ('Order Confirmed','Order Confirmed'),
        ('Out for Delivery','Out for Delivery'),
        ('Delivered','Delivered'),
    )
    customer=models.ForeignKey('Customer', on_delete=models.CASCADE,null=True)
   
    email = models.CharField(max_length=50,null=True)
    address = models.CharField(max_length=500,null=True)
    mobile = models.CharField(max_length=20,null=True)
    order_date= models.DateField(auto_now_add=True,null=True)
    status=models.CharField(max_length=50,null=True,choices=STATUS)
    cart=models.ForeignKey(cart,on_delete=models.CASCADE,null=True)
    
    def update_product_quantities(self):
        # Update product quantities only when the order status changes to 'Order Confirmed'
        if self.status == 'Out for Delivery':
            cart_products = CartProduct.objects.filter(cart=self.cart)
            for cart_product in cart_products:
                product = cart_product.product
                product.quantity -= cart_product.quantity
                product.save()

            # Set the order status to 'Order Confirmed' after updating product quantities
            self.save()
#Sellerss.................


class sellercart(models.Model):
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sellercarts')
    total = models.PositiveIntegerField(default=0)

class Order(models.Model):
    order_id = models.CharField(max_length=100, unique=True)
    total_amount = models.PositiveIntegerField()
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    products = models.ManyToManyField('Product', through='OrderProduct')

    def __str__(self):
        return self.order_id

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return f"Order: {self.order.order_id}, Product: {self.product.name}"

class SellerCartProduct(models.Model):
    cart = models.ForeignKey(sellercart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rate = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField(default=0)
    grade = models.CharField(max_length=500,null=True)

    def __str__(self):
        return "cart:" + str(self.cart.id) + "cartproduct:" + str(self.id)
    

class SellerOrders(models.Model):
    STATUS =(
        ('Pending','Pending'),
        ('Order Confirmed','Order Confirmed'),
        ('Out for Pickup','Out for Pickup'),
        ('Stored in Warehouse','Stored in Warehouse'),
        
    )
    seller=models.ForeignKey('Customer', on_delete=models.CASCADE,null=True)
    email = models.CharField(max_length=50,null=True)
    address = models.CharField(max_length=500,null=True)
    mobile = models.CharField(max_length=20,null=True)
    order_date= models.DateField(auto_now_add=True,null=True)
    status=models.CharField(max_length=50,null=True,choices=STATUS)
    cart=models.ForeignKey(sellercart,on_delete=models.CASCADE,null=True)



