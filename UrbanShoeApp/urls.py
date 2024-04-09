from django.urls import path
from UrbanShoeApp import views
from django.contrib.auth.views import LoginView,LogoutView


urlpatterns = [  
    path('',views.home_view,name=''),
    path('afterlogin', views.afterlogin_view,name='afterlogin'),
    path('logout', LogoutView.as_view(template_name='ecom/logout.html'),name='logout'),
    path('aboutus', views.aboutus_view),
    path('contactus', views.contactus_view,name='contactus'),
    path('search', views.search_view,name='search'),
    path('send-feedback', views.send_feedback_view,name='send-feedback'),
    path('view-feedback', views.view_feedback_view,name='view-feedback'),
path('seller-dashboard/', views.seller_dashboard_view, name='seller-dashboard'),
    path('adminclick', views.adminclick_view),
    path('adminlogin', LoginView.as_view(template_name='ecom/adminlogin.html'),name='adminlogin'),
    path('admin-dashboard', views.admin_dashboard_view,name='admin-dashboard'),
path('edit-order/<int:product_id>/', views.edit_order, name='edit-order'),

path('seller-edit-order/<int:product_id>/', views.seller_edit_order, name='seller-edit-order'),
    path('view-customer', views.view_customer_view,name='view-customer'),
    path('delete-customer/<int:pk>', views.delete_customer_view,name='delete-customer'),
    path('update-customer/<int:pk>', views.update_customer_view,name='update-customer'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment_failure/', views.payment_failure, name='payment_failure'),
    path('order_detail/', views.order_detail, name='order_detail'),
    path('admin-products', views.admin_products_view,name='admin-products'),
    path('admin-add-product', views.admin_add_product_view,name='admin-add-product'),
    path('delete-product/<int:pk>', views.delete_product_view,name='delete-product'),
    path('update-product/<int:pk>', views.update_product_view,name='update-product'),

    path('admin-view-booking', views.admin_view_booking_view,name='admin-view-booking'),
    path('order-pdf/<int:order_id>/', views.generate_pdf, name='order-pdf'),
    path('order-seller-pdf/<int:order_id>/', views.generate_seller_pdf, name='order-seller-pdf'),
    path('admin_view_selling_view', views.admin_view_selling_view,name='admin_view_selling_view'),
    path('delete-order/<int:pk>', views.delete_order_view,name='delete-order'),
    path('delete-seller-order/<int:pk>', views.delete_seller_order_view,name='delete-seller-order'),
    path('update-order/<int:pk>', views.update_order_view,name='update-order'),
    path('update-seller-order/<int:pk>', views.update_seller_order_view,name='update-seller-order'),
    path('customersignup', views.customer_signup_view,name='customersignup'),
    path('customerlogin', LoginView.as_view(template_name='ecom/customerlogin.html'),name='customerlogin'),
    path('customer-home', views.customer_home_view,name='customer-home'),
    path('customer-pdf/<int:order_id>/', views.generate_order_pdf_view, name='customer-pdf'),
    path('seller-pdf/<int:order_id>/', views.generate_sellerorder_pdf_view, name='seller-pdf'),
    path('my-order', views.my_order_view,name='my-order'),
    # path('my-order', views.my_order_view2,name='my-order'),
    path('my-profile', views.my_profile_view,name='my-profile'),
    path('edit-profile', views.edit_profile_view,name='edit-profile'),
    
    path('download-invoice/<int:orderID>/<int:productID>', views.download_invoice_view,name='download-invoice'),


    path('seller-to-cart/<int:pk>', views.seller_to_cart_view,name='seller_cart'),
    path('cart', views.mycart,name='cart'),
     path('cart-seller', views.seller_cart_view,name='cart-seller'),
    path('remove-from-cart/<int:pk>', views.remove_from_cart_view,name='remove-from-cart'),
    path('remove-from-seller/<int:pk>', views.remove_from_cart_seller,name='remove-from-seller'),
    path('customer-address/<int:pk>', views.customer_address_view,name='customer-address'),
    path('payment-success', views.payment_success_view,name='payment-success'),
     path('seller-success', views.seller_success,name='seller-success'),

path('add-to-cart/<int:id>/', views.addtocart, name='add-to-cart'),

   path('my-cart',views.mycart, name='my-cart'),

   path('managecart/<int:id>/',views.managecart,name="managecart"),

path('seller-add-to-cart/<int:id>/', views.selleraddtocart, name='seller-add-to-cart'),

   path('sellercart',views.sellercart, name='sellercart'),

   path('sellermanagecart/<int:id>/',views.sellermanagecart,name="sellermanagecart"),

path('seller-address/<int:pk>', views.seller_address_view,name='seller-address'),
path('seller-order', views.seller_order_view,name='seller-order'),
path('termsnconditions', views.termsnconditions,name='termsnconditions'),
path('analytics', views.analytics,name='analytics'),


]
