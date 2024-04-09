from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.http import HttpResponseRedirect,HttpResponse
from django.core.mail import send_mail
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from django.conf import settings
from django.db.models import Sum
from .models import Order

def home_view(request):
    products = models.Product.objects.all()

    popular_products = models.Product.objects.annotate(num_orders=Count('cartproduct')).order_by('-num_orders')[:5]

    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 0

    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')

    return render(
        request,
        'ecom/index.html',
        {'products': products, 'top_selling_products': popular_products, 'product_count_in_cart': product_count_in_cart}
    )

#for showing login button for admin(by sumit)
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')


def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()


def is_seller(user):
    return user.groups.filter(name='SELLER').exists()


def is_admin(user):
    return user.is_staff

def customer_signup_view(request):
    userForm = forms.CustomerUserForm()
    customerForm = forms.CustomerForm()
    mydict = {'userForm': userForm, 'customerForm': customerForm}

    if request.method == 'POST':
        userForm = forms.CustomerUserForm(request.POST)
        customerForm = forms.CustomerForm(request.POST, request.FILES)

        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()

            customer = customerForm.save(commit=False)
            customer.user = user
            customer.save()

            if customerForm.cleaned_data['user_type'] == 'customer':
                my_customer_group = Group.objects.get_or_create(name='CUSTOMER')
                my_customer_group[0].user_set.add(user)
            elif customerForm.cleaned_data['user_type'] == 'seller':
                my_seller_group = Group.objects.get_or_create(name='SELLER')
                my_seller_group[0].user_set.add(user)

            return HttpResponseRedirect('customerlogin')

    return render(request, 'ecom/customersignup.html', context=mydict)



#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,CUSTOMER

def afterlogin_view(request):
    if is_customer(request.user):
        return redirect('customer-home')
    elif is_seller(request.user):
        return redirect('admin-dashboard')
        # return redirect('seller-dashboard')
        # return redirect('seller-dashboard')  # Change 'seller-dashboard' to your actual seller dashboard URL
    elif is_admin(request.user):
        return redirect('admin-dashboard')
    else:
        messages.error(request, 'Invalid credentials. Please check your username and password.')
        return redirect('customerlogin')


#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    # for cards on dashboard
    customercount = models.Customer.objects.all().count()
    productcount = models.Product.objects.all().count()
    ordercount = models.Orders.objects.all().count()
    sellerordercount=models.SellerOrders.objects.all().count()


    # for recent order tables
    orders = models.Orders.objects.all().order_by('-id')  # Order by id in descending order
    ordered_data = []

    for order in orders:
        cart_products = models.CartProduct.objects.filter(cart=order.cart)
        total_price = order.cart.total  # Fetch total from the cart table
        ordered_data.append({
            'cart_products': cart_products,
            'customer': order.customer,
            'order': order,
            'total_price': total_price,
        })

    mydict = {
        'customercount': customercount,
        'productcount': productcount,
        'ordercount': ordercount,
        'sellerordercount': sellerordercount,
        'data': ordered_data,
        'orders':orders
    }
    
    return render(request, 'ecom/admin_dashboard.html', context=mydict)

def order_detail(request):
    orders_user = Order.objects.all()
    return render(request,'ecom/user_orders.html',{'orders_user':orders_user})

# admin view customer table
@login_required(login_url='adminlogin')
def view_customer_view(request):
    customers=models.Customer.objects.all()
    return render(request,'ecom/view_customer.html',{'customers':customers})

# admin delete customer
@login_required(login_url='adminlogin')
def delete_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return redirect('view-customer')


from django.shortcuts import render, redirect
from . import models, forms
from django.contrib.auth.decorators import login_required

@login_required(login_url='adminlogin')
def update_customer_view(request, pk):
    customer = models.Customer.objects.get(id=pk)
    user = models.User.objects.get(id=customer.user_id)
    userForm = forms.CustomerUserForm(instance=user)
    customerForm = forms.CustomerForm(request.POST or None, instance=customer)
    mydict = {'userForm': userForm, 'customerForm': customerForm}

    if request.method == 'POST':
        userForm = forms.CustomerUserForm(request.POST, instance=user)
        customerForm = forms.CustomerForm(request.POST, instance=customer)

        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(userForm.cleaned_data['password'])
            user.save()
            customerForm.save()
            # Fetch address and phone number from the updated data
            address = customerForm.cleaned_data['address']
            phone_number = customerForm.cleaned_data['mobile']
            return redirect('view-customer')

    return render(request, 'ecom/admin_update_customer.html', context=mydict)

# admin view the product
@login_required(login_url='adminlogin')
def admin_products_view(request):
    products=models.Product.objects.all()
    return render(request,'ecom/admin_products.html',{'products':products})


@login_required(login_url='adminlogin')
def admin_add_product_view(request):
    productForm=forms.ProductForm()
    if request.method=='POST':
        productForm=forms.ProductForm(request.POST, request.FILES)
        if productForm.is_valid():
            productForm.save()
        return HttpResponseRedirect('admin-products')
    return render(request,'ecom/admin_add_products.html',{'productForm':productForm})

@login_required(login_url='adminlogin')
def delete_product_view(request,pk):
    product=models.Product.objects.get(id=pk)
    product.delete()
    return redirect('admin-products')


@login_required(login_url='adminlogin')
def update_product_view(request,pk):
    product=models.Product.objects.get(id=pk)
    productForm=forms.ProductForm(instance=product)
    if request.method=='POST':
        productForm=forms.ProductForm(request.POST,request.FILES,instance=product)
        if productForm.is_valid():
            productForm.save()
            return redirect('admin-products')
    return render(request,'ecom/admin_update_product.html',{'productForm':productForm})


@login_required(login_url='adminlogin')
def admin_view_booking_view(request):
    orders = models.Orders.objects.all().order_by('-id')  # Order by id in descending order
    ordered_data = []

    for order in orders:
        # Fetch latest cart products from the database
        cart_products = models.CartProduct.objects.filter(cart=order.cart)
        total_price = order.cart.total  # Fetch total from the cart table
        ordered_data.append({
            'cart_products': cart_products,
            'customer': order.customer,
            'order': order,
            'total_price': total_price,
        })

    return render(request, 'ecom/admin_view_booking.html', {'data': ordered_data})

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from . import models

def generate_pdf(request, order_id):
    # Get the order details
    order = get_object_or_404(models.Orders, id=order_id)
    cart_products = models.CartProduct.objects.filter(cart=order.cart)

    # Prepare data to pass to the template
    context = {
        'order': order,
        'cart_products': cart_products,
    }

    # Render the template
    template = get_template('ecom/order_pdf.html')
    html = template.render(context)

    # Create a PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order.id}.pdf"'

    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response



@login_required(login_url='adminlogin')
def admin_view_selling_view(request):
    orders = models.SellerOrders.objects.all().order_by('-id')  # Order by id in descending order
    ordered_data = []

    for order in orders:
        # Fetch latest cart products from the database
        cart_products = models.SellerCartProduct.objects.filter(cart=order.cart)
        total_price = order.cart.total  # Fetch total from the cart table
        

        ordered_data.append({
            'cart_products': cart_products,
            'customer': order.seller,
            'order': order,
            'total_price': total_price,
             # Include grade details in the ordered data
        })

    return render(request, 'ecom/admin_view_sellers.html', {'data': ordered_data})


from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from . import models

def generate_seller_pdf(request, order_id):
    # Get the order details
    order = get_object_or_404(models.SellerOrders, id=order_id)
    cart_products = models.SellerCartProduct.objects.filter(cart=order.cart)

    # Prepare data to pass to the template
    context = {
        'order': order,
        'cart_products': cart_products,
    }

    # Render the template
    template = get_template('ecom/order_seller_pdf.html')
    html = template.render(context)

    # Create a PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order.id}.pdf"'

    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response

    

@login_required(login_url='adminlogin')
def delete_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    order.delete()
    return redirect('admin-view-booking')

@login_required(login_url='adminlogin')
def delete_seller_order_view(request,pk):
    order=models.SellerOrders.objects.get(id=pk)
    order.delete()
    return redirect('admin_view_selling_view')


# Add this function to your views
def calculate_updated_total(order):
    cart_products = models.CartProduct.objects.filter(cart=order.cart)
    total = sum(cart_product.subtotal for cart_product in cart_products)
    return total


# for changing status of order (pending, delivered...)


from django.db import transaction
from django.db.models import F


@login_required(login_url='adminlogin')
def update_order_view(request, pk):
    order = models.Orders.objects.get(id=pk)
    cart_products = models.CartProduct.objects.filter(cart=order.cart)

    # Fetch additional details for display
    order_details = {
        'order_id': order.id,
        'customer_name': order.customer.get_name,
        'order_date': order.order_date,
    }

    initial_data = {
        'address': order.address,
        'mobile': order.mobile,
        'status': order.status,
        'total': order.cart.total,
    }

    if request.method == 'POST':
        order_form = forms.OrderForm(request.POST, instance=order)

        if order_form.is_valid():
            with transaction.atomic():
                # Update CartProduct details
                for cart_product in cart_products:
                    # Existing product details
                    product_name_key = f'product_{cart_product.id}'
                    cart_product.product.name = request.POST.get(product_name_key, cart_product.product.name)

                    cart_product.rate = float(request.POST.get(f'rate_{cart_product.id}', 0))
                    cart_product.quantity = int(request.POST.get(f'quantity_{cart_product.id}', 0))

                    # Convert subtotal to float before assigning
                    cart_product.subtotal = float(request.POST.get(f'subtotal_{cart_product.id}', 0))

                    cart_product.save()

                    # Delete product if the corresponding checkbox is checked
                    if request.POST.get(f'delete_product_{cart_product.id}'):
                        cart_product.delete()

                # Add new product if the 'add_new_product' checkbox is checked
                if 'add_new_product' in request.POST:
                    new_product_name = request.POST.get('new_product_name')
                    new_rate = float(request.POST.get('new_rate', 0))
                    new_quantity = int(request.POST.get('new_quantity', 0))
                    new_subtotal = new_rate * new_quantity

                    # Create a new CartProduct for the new product
                    new_cart_product = models.CartProduct.objects.create(
                        cart=order.cart,
                        product=models.Product.objects.create(name=new_product_name),
                        rate=new_rate,
                        quantity=new_quantity,
                        subtotal=new_subtotal,
                    )

                # Check if the status is changed to 'Out for Delivery'
                if order_form.cleaned_data['status'] == 'Out for Delivery':
                    # Update product quantities using F() expression
                    for cart_product in cart_products:
                        product = cart_product.product
                        product.quantity -= cart_product.quantity
                        product.save()

                # Update associated Cart total after updating CartProduct details
                order.cart.total = calculate_updated_total(order)
                order.cart.save()

                # Save the main form
                order_form.save()

                # Redirect to admin_view_booking_view with updated data
                return redirect('admin-view-booking')

    else:
        order_form = forms.OrderForm(instance=order, initial=initial_data)

    return render(request, 'ecom/update_order.html', {'orderForm': order_form, 'cart_products': cart_products, 'order_details': order_details})



from django.shortcuts import render, get_object_or_404, redirect
@login_required(login_url='adminlogin')
def edit_order(request, product_id):
    product = get_object_or_404(models.CartProduct, id=product_id)
    
    if request.method == 'POST':
        form = forms.EditOrderForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('admin-view-booking')  # Replace 'your-success-url' with the actual URL to redirect after successful edit
    else:
        form = forms.EditOrderForm(instance=product)

    return render(request, 'ecom/edit_order.html', {'form': form, 'product': product})

@login_required(login_url='adminlogin')
def delete_product_from_order(request, order_id, product_id):
    order = get_object_or_404(models.Orders, id=order_id)
    product = get_object_or_404(models.CartProduct, id=product_id)

    # Ensure the product is associated with the given order
    if product.cart == order.cart:
        product.delete()

    return redirect('admin-view-booking')


from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from . import models, forms

def calculate_updated_seller_total(order):
    cart_products = models.SellerCartProduct.objects.filter(cart=order.cart)
    total = sum(cart_product.subtotal for cart_product in cart_products)
    return total

@login_required(login_url='adminlogin')
def update_seller_order_view(request, pk):
    order = models.SellerOrders.objects.get(id=pk)
    cart_products = models.SellerCartProduct.objects.filter(cart=order.cart)

    order_details = {
        'order_id': order.id,
        'customer_name': order.seller.get_name,
        'order_date': order.order_date,
    }

    initial_data = {
        'address': order.address,
        'mobile': order.mobile,
        'status': order.status,
        'total': order.cart.total,
    }

    if request.method == 'POST':
        order_form = forms.SellerOrderForm(request.POST, instance=order)

        if order_form.is_valid():
            with transaction.atomic():
                for cart_product in cart_products:
                    cart_product.product.name = request.POST.get(f'product_{cart_product.id}')
                    cart_product.rate = float(request.POST.get(f'rate_{cart_product.id}', 0))
                    cart_product.quantity = int(request.POST.get(f'quantity_{cart_product.id}', 0))
                    cart_product.grade = request.POST.get(f'grade_{cart_product.id}')
                    cart_product.subtotal = float(request.POST.get(f'subtotal_{cart_product.id}', 0))
                    cart_product.save()

                    if f'delete_product_{cart_product.id}' in request.POST:
                        cart_product.delete()

                if 'add_new_product' in request.POST:
                    new_product_name = request.POST.get('new_product_name')
                    new_cart_product = models.SellerCartProduct.objects.create(
                        cart=order.cart,
                        product=models.Product.objects.create(name=new_product_name),
                        rate=float(request.POST.get('new_rate', 0)),
                        quantity=int(request.POST.get('new_quantity', 0)),
                        subtotal=float(request.POST.get('new_subtotal', 0)),
                    )

                # Update associated Cart total after updating CartProduct details
                order.cart.total = calculate_updated_seller_total(order)
                order.cart.save()

                # Save the main form
                order_form.save()

                return redirect('admin_view_selling_view')

    else:
        order_form = forms.SellerOrderForm(instance=order, initial=initial_data)

    return render(request, 'ecom/update_seller_order.html', {'orderForm': order_form, 'cart_products': cart_products, 'order_details': order_details})



from django.shortcuts import render, get_object_or_404, redirect
@login_required(login_url='adminlogin')
def seller_edit_order(request, product_id):
    product = get_object_or_404(models.SellerCartProduct, id=product_id)
    
    if request.method == 'POST':
        form = forms.SellerEditOrderForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('admin_view_selling_view')  # Replace 'your-success-url' with the actual URL to redirect after successful edit
    else:
        form = forms.SellerEditOrderForm(instance=product)

    return render(request, 'ecom/selleredit_order.html', {'form': form, 'product': product})

# admin view the feedback
@login_required(login_url='adminlogin')
def view_feedback_view(request):
    feedbacks=models.Feedback.objects.all().order_by('-id')
    return render(request,'ecom/view_feedback.html',{'feedbacks':feedbacks})



#---------------------------------------------------------------------------------
#------------------------ PUBLIC CUSTOMER RELATED VIEWS START ---------------------
#---------------------------------------------------------------------------------
def search_view(request):
    # whatever user write in search box we get in query
    query = request.GET['query']
    products=models.Product.objects.all().filter(name__icontains=query)
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    # word variable will be shown in html when user click on search button
    word="Searched Result :"

    if request.user.is_authenticated:
        return render(request,'ecom/customer_home.html',{'products':products,'word':word,'product_count_in_cart':product_count_in_cart})
    return render(request,'ecom/index.html',{'products':products,'word':word,'product_count_in_cart':product_count_in_cart})


# any one can add product to cart, no need of signin
def add_to_cart_view(request,pk):
    products=models.Product.objects.all()

    #for cart counter, fetching products ids added by customer from cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=1

    response = render(request, 'ecom/index.html',{'products':products,'product_count_in_cart':product_count_in_cart})

    #adding product id to cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids=="":
            product_ids=str(pk)
        else:
            product_ids=product_ids+"|"+str(pk)
        response.set_cookie('product_ids', product_ids)
    else:
        response.set_cookie('product_ids', pk)

    product=models.Product.objects.get(id=pk)
    messages.info(request, product.name + ' added to cart successfully!')

    return response



 #For checkout of cart
def cart_view(request):
    # For cart counter
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 0

    # Fetching product details from the database whose id is present in cookies
    products = None
    total = 0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart = product_ids.split('|')
            products = models.Product.objects.filter(id__in=product_id_in_cart)
            # Calculate total price for each product
            for p in products:
                p.total_price = p.price * p.quantity
                total += p.total_price
    return render(request, 'ecom/cart.html', {'products': products, 'total': total, 'product_count_in_cart': product_count_in_cart})


def remove_from_cart_view(request, pk):
    # For counter in cart
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 0

    # Removing product id from the cookie
    total = 0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        product_id_in_cart = product_ids.split('|')
        product_id_in_cart = list(set(product_id_in_cart))
        product_id_in_cart.remove(str(pk))
        products = models.Product.objects.all().filter(id__in=product_id_in_cart)
        # For the total price shown in the cart after removing the product
        for p in products:
            total = total + p.price * p.quantity

        # For updating the cookie value after removing the product id in the cart
        value = "|".join(product_id_in_cart)
        response = render(request, 'ecom/cart.html', {'products': products, 'total': total, 'product_count_in_cart': product_count_in_cart})
        if not value:
            response.delete_cookie('product_ids')
        response.set_cookie('product_ids', value)
        return response


def send_feedback_view(request):
    feedbackForm=forms.FeedbackForm()
    if request.method == 'POST':
        feedbackForm = forms.FeedbackForm(request.POST)
        if feedbackForm.is_valid():
            feedbackForm.save()
            return render(request, 'ecom/feedback_sent.html')
    return render(request, 'ecom/send_feedback.html', {'feedbackForm':feedbackForm})


#---------------------------------------------------------------------------------
#------------------------ CUSTOMER RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_home_view(request):
    products = models.Product.objects.all()
    
    # For cart counter
    cart_id = request.session.get('cart_id')
    if cart_id:
        cart1 = models.cart.objects.get(id=cart_id)
        product_count_in_cart = cart1.cartproduct_set.count()  # Get the count of items in the cart
    else:
        product_count_in_cart = 0
    return render(request, 'ecom/customer_home.html', {'products': products, 'product_count_in_cart': product_count_in_cart})


from django.db import transaction
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from . import forms
from . import models
import razorpay


@login_required(login_url='customerlogin')
def customer_address_view(request, pk):
    addressForm = forms.AddressForm()
    user = request.user
    customer = models.Customer.objects.get(user=user)
    cart_obj = models.cart.objects.get(id=pk)

    if request.method == 'POST':
        addressForm = forms.AddressForm(request.POST)
        if addressForm.is_valid():
            email = addressForm.cleaned_data['Email']
            mobile = addressForm.cleaned_data['Mobile']
            address = addressForm.cleaned_data['Address']

            # Create an order and link it to the customer and cart
            new_order = models.Orders.objects.create(
                customer=customer, email=email, address=address, mobile=mobile, status='Pending', cart=cart_obj
            )


            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            # Calculate total amount
            total_amount = cart_obj.total * 100  # Convert to paisa

            # Create Razorpay order
            razorpay_order = client.order.create({
                'amount': total_amount,
                'currency': 'INR',
                'receipt': str(new_order.id),  # Set order ID as receipt
                'payment_capture': '1'
            })

            # Save Razorpay order ID to the order
            new_order.razorpay_order_id = razorpay_order['id']
            new_order.save()

            # Redirect to Razorpay payment page
            return render(request, 'ecom/payment_page.html', {'order_id': new_order.id, 'razorpay_order_id': razorpay_order['id'], 'amount': total_amount})

    return render(request, 'ecom/customer_address.html', {'addressForm': addressForm})

from .models import CartProduct
from .models import cart

def payment_success(request):
    if request.method == 'POST':

        return redirect('payment_failure')


    else:
        # If the request method is not POST, redirect to some other page or show an error
        response=HttpResponseRedirect('my-order')
        response.delete_cookie('product_ids')
        user = request.user
        try:
            # Retrieve all carts associated with the user
            user_carts = cart.objects.filter(customer=user)

            # Loop through each cart and delete associated cart products
            for user_cart in user_carts:
                # Retrieve cart products associated with the user's cart
                cart_products = CartProduct.objects.filter(cart=user_cart)



            # Optionally, you can add a success message
            messages.success(request, 'Payment successful! Your selected cart products have been cleared.')

        except cart.DoesNotExist:
            # Handle the case if the user does not have a cart
            messages.error(request, 'Payment successful, but no cart items were found.')
            pass

        return redirect('my-order')

def payment_failure(request):
    return render(request,'ecom/payment_failure.html')
# here we are just directing to this view...actually we have to check whther payment is successful or not
#then only this view should be accessed
@login_required(login_url='customerlogin')
def payment_success_view(request):
    # Here we will place order | after successful payment
    # we will fetch customer  mobile, address, Email
    # we will fetch product id from cookies then respective details from db
    # then we will create order objects and store in db
    # after that we will delete cookies because after order placed...cart should be empty
    customer=models.Customer.objects.get(user_id=request.user.id)
    products=None
    email=None
    mobile=None
    address=None
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart=product_ids.split('|')
            products=models.Product.objects.all().filter(id__in = product_id_in_cart)
            # Here we get products list that will be ordered by one customer at a time

    # these things can be change so accessing at the time of order...
    if 'email' in request.COOKIES:
        email=request.COOKIES['email']
    if 'mobile' in request.COOKIES:
        mobile=request.COOKIES['mobile']
    if 'address' in request.COOKIES:
        address=request.COOKIES['address']

    # here we are placing number of orders as much there is a products
    # suppose if we have 5 items in cart and we place order....so 5 rows will be created in orders table
    # there will be lot of redundant data in orders table...but its become more complicated if we normalize it
    for product in products:
        models.Orders.objects.get_or_create(customer=customer,product=product,status='Pending',email=email,mobile=mobile,address=address)

    # after order placed cookies should be deleted
    response = render(request,'ecom/payment_success.html')
    response.delete_cookie('product_ids')
    response.delete_cookie('email')
    response.delete_cookie('mobile')
    response.delete_cookie('address')
    return response




def generate_customer_order_pdf(order):
    cart_products = models.CartProduct.objects.filter(cart=order.cart)

    # Prepare data to pass to the template
    context = {
        'order': order,
        'cart_products': cart_products,
    }

    # Render the template
    template = get_template('ecom/customer_pdf.html')
    html = template.render(context)

    # Create a PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order.id}.pdf"'

    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response

@login_required(login_url='customerlogin')
@user_passes_test(lambda u: u.customer.user_type == 'customer', login_url='customerlogin')
def my_order_view(request):
    customer = models.Customer.objects.get(user=request.user)
    orders = models.Orders.objects.filter(customer=customer).order_by('-id')  # Order by id in descending order
    ordered_products = []
    print(orders)

    for order in orders:
        cart_products = models.CartProduct.objects.filter(cart=order.cart)
        products = []

        for cart_product in cart_products:
            product_info = {
                'name': cart_product.product.name,
                'description': cart_product.product.description,
                'price': cart_product.product.price,
                'quantity': cart_product.quantity,
                'subtotal': cart_product.subtotal,
            }
            products.append(product_info)

        ordered_products.append({
            'order': order,
            'products': products,
        })

    return render(request, 'ecom/my_order.html', {'data': ordered_products, 'customer': customer})

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def generate_order_pdf_view(request, order_id):
    order = get_object_or_404(models.Orders, id=order_id)
    return generate_customer_order_pdf(order)
# @login_required(login_url='customerlogin')
# @user_passes_test(is_customer)
# def my_order_view2(request):

#     products=models.Product.objects.all()
#     if 'product_ids' in request.COOKIES:
#         product_ids = request.COOKIES['product_ids']
#         counter=product_ids.split('|')
#         product_count_in_cart=len(set(counter))
#     else:
#         product_count_in_cart=0
#     return render(request,'ecom/my_order.html',{'products':products,'product_count_in_cart':product_count_in_cart})    



#--------------for discharge patient bill (pdf) download and printing
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.http import HttpResponse, Http404


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def download_invoice_view(request, orderID, productID):
    try:
        order = models.Orders.objects.get(id=orderID)
        product = models.Product.objects.get(id=productID)

        mydict = {
            'orderDate': order.order_date,
            'customerName': request.user,
            'customerEmail': order.email,
            'customerMobile': order.mobile,
            'shipmentAddress': order.address,
            'orderStatus': order.status,
            'productName': product.name,
            'productImage': product.product_image,
            'productPrice': product.price,
            'productDescription': product.description,
        }

        return render_to_pdf('ecom/download_invoice.html', mydict)

    except (models.Orders.DoesNotExist, models.Product.DoesNotExist):
        raise Http404("Order or Product does not exist")




@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    return render(request,'ecom/my_profile.html',{'customer':customer})


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def edit_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return HttpResponseRedirect('my-profile')
    return render(request,'ecom/edit_profile.html',context=mydict)




@login_required(login_url='customerlogin')
@user_passes_test(is_seller)
def seller_dashboard_view(request):
    # Fetch the current seller
    seller = models.Customer.objects.get(user_id=request.user.id)
    # Retrieve all products regardless of the seller
    products = models.Product.objects.all()
    # For cart counter
    cart_id = request.session.get('cart_id')
    print(f'cart_id: {cart_id}')
    if cart_id:
        try:
            # Change the model name to sellercart
            cart1 = models.sellercart.objects.get(id=cart_id)
            print(f'cart1: {cart1}')
            product_count_in_cart = cart1.sellercartproduct_set.count()
            print(f'product_count_in_cart: {product_count_in_cart}')
        except models.sellercart.DoesNotExist:
            print('Cart does not exist')
            product_count_in_cart = 0
    else:
        product_count_in_cart = 0
    return render(request, 'ecom/seller_dashboard.html', {'customer': seller, 'products': products, 'product_count_in_cart': product_count_in_cart})

def seller_cart_view(request):
    # For cart counter
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 0

    # Fetching product details from the database whose id is present in cookies
    products = None
    total = 0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart = product_ids.split('|')
            products = models.Product.objects.filter(id__in=product_id_in_cart)
            # Calculate total price for each product
            for p in products:
                p.total_price = p.price * p.quantity
                total += p.total_price
    return render(request, 'ecom/seller_cart.html', {'products': products, 'total': total, 'product_count_in_cart': product_count_in_cart})




def seller_to_cart_view(request,pk):
    products=models.Product.objects.all()

    #for cart counter, fetching products ids added by customer from cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=1

    response = render(request, 'ecom/seller_cart.html',{'products':products,'product_count_in_cart':product_count_in_cart})

    #adding product id to cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids=="":
            product_ids=str(pk)
        else:
            product_ids=product_ids+"|"+str(pk)
        response.set_cookie('product_ids', product_ids)
    else:
        response.set_cookie('product_ids', pk)

    product=models.Product.objects.get(id=pk)
    messages.info(request, product.name + ' added to cart successfully!')

    return response



 #For checkout of cart
def cart_seller(request):
    # For cart counter
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 0

    # Fetching product details from the database whose id is present in cookies
    products = None
    total = 0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart = product_ids.split('|')
            products = models.Product.objects.filter(id__in=product_id_in_cart)
            # Calculate total price for each product
            for p in products:
                p.total_price = p.price * p.quantity
                total += p.total_price
    return render(request, 'ecom/seller_cart.html', {'products': products, 'total': total, 'product_count_in_cart': product_count_in_cart})


def remove_from_cart_seller(request, pk):
    # For counter in cart
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 0

    # Removing product id from the cookie
    total = 0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        product_id_in_cart = product_ids.split('|')
        product_id_in_cart = list(set(product_id_in_cart))

        # Check if the product ID is in the list before removing
        if str(pk) in product_id_in_cart:
            product_id_in_cart.remove(str(pk))

        products = models.Product.objects.all().filter(id__in=product_id_in_cart)

        # For the total price shown in the cart after removing the product
        for p in products:
            total += p.price * p.quantity

        # For updating the cookie value after removing the product id in the cart
        value = "|".join(product_id_in_cart)
        response = render(request, 'ecom/seller_cart.html', {'products': products, 'total': total, 'product_count_in_cart': product_count_in_cart})

        if not value:
            response.delete_cookie('product_ids')
        response.set_cookie('product_ids', value)
        return response



@login_required(login_url='customerlogin')
@user_passes_test(is_seller)
def seller_success(request):
    # Here we will place order | after successful payment
    # we will fetch customer  mobile, address, Email
    # we will fetch product id from cookies then respective details from db
    # then we will create order objects and store in db
    # after that we will delete cookies because after order placed...cart should be empty
    seller=models.Customer.objects.get(user_id=request.user.id)
    products=None
    email=None
    mobile=None
    address=None
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart=product_ids.split('|')
            products=models.Product.objects.all().filter(id__in = product_id_in_cart)
            # Here we get products list that will be ordered by one customer at a time

    # these things can be change so accessing at the time of order...
    if 'email' in request.COOKIES:
        email=request.COOKIES['email']
    if 'mobile' in request.COOKIES:
        mobile=request.COOKIES['mobile']
    if 'address' in request.COOKIES:
        address=request.COOKIES['address']

    # here we are placing number of orders as much there is a products
    # suppose if we have 5 items in cart and we place order....so 5 rows will be created in orders table
    # there will be lot of redundant data in orders table...but its become more complicated if we normalize it
    for product in products:
        models.SellerOrders.objects.get_or_create(seller=seller,product=product,status='Pending',email=email,mobile=mobile,address=address)

    # after order placed cookies should be deleted
    response = render(request,'ecom/seller_success.html')
    response.delete_cookie('product_ids')
    response.delete_cookie('email')
    response.delete_cookie('mobile')
    response.delete_cookie('address')
    return response




#---------------------------------------------------------------------------------
#------------------------ ABOUT US AND CONTACT US VIEWS START --------------------
#---------------------------------------------------------------------------------
def aboutus_view(request):
    products = models.Product.objects.all()
    return render(request,'ecom/aboutus.html',{'products': products})

def termsnconditions(request):
    return render(request,'ecom/terms.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message, settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'ecom/contactussuccess.html')
    return render(request, 'ecom/contactus.html', {'form':sub})


#my edit works

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)

def mycart(request):
    try:
        user_id = request.user
        up = models.Customer.objects.get(user=user_id)
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart1 = models.cart.objects.get(id=cart_id)
            product_count_in_cart = cart1.cartproduct_set.count()  # Get the count of items in the cart
        else:
            cart1 = None
            product_count_in_cart = 0
        context = {'cart': cart1, 'u': up, 'product_count_in_cart': product_count_in_cart}
        return render(request, 'ecom/cart.html', context)
    except models.Customer.DoesNotExist:
        # User is not a customer, redirect to login page with an error message
        messages.error(request, 'You need to log in as a customer to view your cart.')
        return redirect('customerlogin')
    

        

@login_required(login_url='customerlogin')
def addtocart(request, id):
    product_obj = models.Product.objects.get(id=id)

    # check if the cart exists

    cart_id = request.session.get('cart_id')
    if cart_id:

        cart_obj = models.cart.objects.get(id=cart_id)
        product_in_cart = cart_obj.cartproduct_set.filter(product=product_obj)
        # item already exist in cart
        if product_in_cart.exists():
            cartproduct = product_in_cart.last()
            cartproduct.quantity += 1
            cartproduct.subtotal += product_obj.price
            cartproduct.save()
            cart_obj.total += product_obj.price
            cart_obj.save()
        else:
            cartproduct = models.CartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.price,
                                                     quantity=1, subtotal=product_obj.price)
            cart_obj.total += product_obj.price
            cart_obj.save()
    else:
        user_id = request.user
        


        cart_obj = models.cart.objects.create(customer=user_id,total=0)
        request.session['cart_id'] = cart_obj.id
        print("new cart")
        cp = models.CartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.price, quantity=1,
                                                 subtotal=product_obj.price)
        cart_obj.total += product_obj.price
        cart_obj.save()

    return redirect('customer-home')

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def managecart(request, id):
    print("im in manage cart")
    action = request.GET.get("action")
    cp_obj = models.CartProduct.objects.get(id=id)
    cart_obj = cp_obj.cart

    if action == "inc":
        cp_obj.quantity += 1
        

        cp_obj.subtotal += cp_obj.rate
        cp_obj.save()
        cart_obj.total += cp_obj.rate
        cart_obj.save()
    elif action == "dcr":
        cp_obj.quantity -= 1
        cp_obj.subtotal -= cp_obj.rate
        cp_obj.save()
        cart_obj.total -= cp_obj.rate
        cart_obj.save()
        if cp_obj.quantity == 0:
            cp_obj.delete()


    elif action == 'rmv':
        cart_obj.total -= cp_obj.subtotal
        cart_obj.save()
        cp_obj.delete()
    else:
        pass

    return redirect('/my-cart')



#Seller

@login_required(login_url='customerlogin')
def sellercart(request):
    user_id = request.user
    up = models.Customer.objects.get(user=user_id)
    cart_id = request.session.get('cart_id')
    if cart_id:
        cart1 = models.sellercart.objects.get(id=cart_id)
    else:
        cart1 = None
    context = {'cart': cart1,'u':up}


    return render(request, 'ecom/seller_cart.html', context)


@login_required(login_url='customerlogin')
def selleraddtocart(request, id):
    product_obj = models.Product.objects.get(id=id)

    # check if the cart exists
    cart_id = request.session.get('cart_id')

    if cart_id:
        cart_obj = models.sellercart.objects.get(id=cart_id)
        product_in_cart = cart_obj.sellercartproduct_set.filter(product=product_obj)

        # item already exists in cart
        if product_in_cart.exists():
            cartproduct = product_in_cart.last()
            cartproduct.quantity += 1
            cartproduct.save()
        else:
            cartproduct = models.SellerCartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.price,
                                                     quantity=1)
            
        cart_obj.save()
    else:
        user_id = request.user
        cart_obj = models.sellercart.objects.create(seller=user_id)
        request.session['cart_id'] = cart_obj.id
        print("new cart")
        cp = models.SellerCartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.price, quantity=1)
        cart_obj.save()

    return redirect('seller-dashboard')


@login_required(login_url='customerlogin')
def sellermanagecart(request, id):
    print("im in manage cart")
    action = request.GET.get("action")
    cp_obj = models.SellerCartProduct.objects.get(id=id)
    cart_obj = cp_obj.cart

    if action == "inc":
        cp_obj.quantity += 1
        cp_obj.save()
    elif action == "dcr":
        cp_obj.quantity -= 1
        cp_obj.save()
        if cp_obj.quantity == 0:
            cp_obj.delete()
    elif action == 'rmv':
        cp_obj.delete()
    else:
        pass

    cart_obj.save()

    return redirect('/sellercart')


@login_required(login_url='customerlogin')
def seller_address_view(request,pk):
    # this is for checking whether product is present in cart or not
    # if there is no product in cart we will not show address form
   
    addressForm = forms.AddressForm()
    user=request.user
    customer=models.Customer.objects.get(user=user)
    cart_obj=models.sellercart.objects.get(id=pk)
    if request.method == 'POST':
        addressForm = forms.AddressForm(request.POST)
        if addressForm.is_valid():
            # here we are taking address, email, mobile at time of order placement
            # we are not taking it from customer account table because
            # these thing can be changes
            email = addressForm.cleaned_data['Email']
            mobile=addressForm.cleaned_data['Mobile']
            address = addressForm.cleaned_data['Address']
            #for showing total price on payment page.....accessing id from cookies then fetching  price of product from db
            new=models.SellerOrders.objects.create(seller=customer,address=address,mobile=mobile,status='Order Confirmed',cart=cart_obj)
            new.save()
            del request.session['cart_id']
            return redirect('seller-order')
           
    return render(request,'ecom/seller_address.html',{'addressForm':addressForm})



def generate_seller_order_pdf(order):
    cart_products = models.SellerCartProduct.objects.filter(cart=order.cart)

    # Prepare data to pass to the template
    context = {
        'order': order,
        'cart_products': cart_products,
    }

    # Render the template
    template = get_template('ecom/seller_pdf.html')
    html = template.render(context)

    # Create a PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order.id}.pdf"'

    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response


@login_required(login_url='customerlogin')
@user_passes_test(is_seller)
def seller_order_view(request):
    seller = models.Customer.objects.get(user_id=request.user.id)
    orders = models.SellerOrders.objects.filter(seller=seller).order_by('-id')  # Order by id in descending order
    ordered_products = []

    for order in orders:
        cart_products = models.SellerCartProduct.objects.filter(cart=order.cart)
        products = []

        for cart_product in cart_products:
            product_info = {
                'name': cart_product.product.name,
                'description': cart_product.product.description,
                'price': cart_product.product.price,
                'quantity': cart_product.quantity,
                'subtotal': cart_product.subtotal,
                'grade': cart_product.grade,
            }
            products.append(product_info)

        ordered_products.append({
            'order': order,
            'products': products,
        })

    return render(request, 'ecom/seller_order.html', {'data': ordered_products, 'customer': seller})


@login_required(login_url='customerlogin')
@user_passes_test(is_seller)
def generate_sellerorder_pdf_view(request, order_id):
    order = get_object_or_404(models.SellerOrders, id=order_id)
    return generate_seller_order_pdf(order)

from django.db.models import Count, Sum
from django.shortcuts import render
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from . import models
from django.db.models import Prefetch

@login_required(login_url='adminlogin')
def analytics(request):
    # Get delivered customer orders
    delivered_customer_orders = models.Orders.objects.filter(status='Delivered')
    customer_today_income = delivered_customer_orders.filter(order_date=datetime.today()).aggregate(Sum('cart__total'))['cart__total__sum'] or 0
    customer_yesterday_income = delivered_customer_orders.filter(order_date=datetime.today() - timedelta(days=1)).aggregate(Sum('cart__total'))['cart__total__sum'] or 0
    customer_last_week_income = delivered_customer_orders.filter(order_date__gte=datetime.today() - timedelta(days=7), order_date__lt=datetime.today()).aggregate(Sum('cart__total'))['cart__total__sum'] or 0
    customer_last_month_income = delivered_customer_orders.filter(order_date__month=(datetime.today() - timedelta(days=30)).month).aggregate(Sum('cart__total'))['cart__total__sum'] or 0
    customer_last_year_income = delivered_customer_orders.filter(order_date__year=(datetime.today() - timedelta(days=365)).year).aggregate(Sum('cart__total'))['cart__total__sum'] or 0

    # Get delivered seller orders
    delivered_seller_orders = models.SellerOrders.objects.filter(status='Stored in Warehouse')
    seller_today_income = delivered_seller_orders.filter(order_date=datetime.today()).aggregate(Sum('cart__total'))['cart__total__sum'] or 0
    seller_yesterday_income = delivered_seller_orders.filter(order_date=datetime.today() - timedelta(days=1)).aggregate(Sum('cart__total'))['cart__total__sum'] or 0
    seller_last_week_income = delivered_seller_orders.filter(order_date__gte=datetime.today() - timedelta(days=7), order_date__lt=datetime.today()).aggregate(Sum('cart__total'))['cart__total__sum'] or 0
    seller_last_month_income = delivered_seller_orders.filter(order_date__month=(datetime.today() - timedelta(days=30)).month).aggregate(Sum('cart__total'))['cart__total__sum'] or 0
    seller_last_year_income = delivered_seller_orders.filter(order_date__year=(datetime.today() - timedelta(days=365)).year).aggregate(Sum('cart__total'))['cart__total__sum'] or 0

  
    popular_products = models.Product.objects.annotate(num_orders=Count('cartproduct')).order_by('-num_orders')[:3]

    # Additional analytics for sellers
    top_selling_products = models.Product.objects.annotate(num_orders=Count('sellercartproduct')).order_by('-num_orders')[:3]

    return render(request, 'ecom/analytics.html', {
        'customer_today_income': customer_today_income,
        'customer_yesterday_income': customer_yesterday_income,
        'customer_last_week_income': customer_last_week_income,
        'customer_last_month_income': customer_last_month_income,
        'customer_last_year_income': customer_last_year_income,
        'seller_today_income': seller_today_income,
        'seller_yesterday_income': seller_yesterday_income,
        'seller_last_week_income': seller_last_week_income,
        'seller_last_month_income': seller_last_month_income,
        'seller_last_year_income': seller_last_year_income,
        'popular_products': popular_products,
        'top_selling_products': top_selling_products,
    })
