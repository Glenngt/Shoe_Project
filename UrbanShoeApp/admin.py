from django.contrib import admin
from .models import Customer,Product,Orders,Feedback
from . models import *
# Register your models here.
class CustomerAdmin(admin.ModelAdmin):
    pass
admin.site.register(Customer, CustomerAdmin)

class ProductAdmin(admin.ModelAdmin):
    pass
admin.site.register(Product, ProductAdmin)

class OrderAdmin(admin.ModelAdmin):
    pass
admin.site.register(Orders, OrderAdmin)

class FeedbackAdmin(admin.ModelAdmin):
    pass
admin.site.register(Feedback, FeedbackAdmin)
# Register your models here.
admin.site.register(cart)
admin.site.register(CartProduct)

admin.site.register(sellercart)
admin.site.register(SellerCartProduct)
class OrderAdmin(admin.ModelAdmin):
    pass
admin.site.register(SellerOrders, OrderAdmin)