from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Product, ProductImage, Category, Customer, Order, OrderItem
from .forms import CustomerRegistrationForm, CustomerLoginForm, ShippingForm, CustomerProfileForm, AdminRegistrationForm
import os
from django.core.mail import send_mail
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.contrib import messages
from django.conf import settings

def home(request):
    # Get all categories for the filter
    categories = Category.objects.all()

    # Get distinct sizes and colors from products
    sizes = Product.objects.values_list('size', flat=True).distinct().exclude(size__isnull=True).exclude(size__exact='')
    colors = Product.objects.values_list('color', flat=True).distinct().exclude(color__isnull=True).exclude(color__exact='')

    # Get filter parameters from the request
    category_ids = request.GET.getlist('category')
    price_ranges = request.GET.getlist('price_range')
    selected_sizes = request.GET.getlist('size')
    selected_colors = request.GET.getlist('color')
    search_query = request.GET.get('search', '')

    # Start with all products
    products = Product.objects.all()

    # Apply search filter
    if search_query:
        products = products.filter(name__icontains=search_query)

    # Apply category filter
    if category_ids:
        products = products.filter(category__id__in=category_ids)

    # Apply price range filter
    if price_ranges:
        price_filters = []
        for price_range in price_ranges:
            if price_range == "0-500":
                price_filters.append((0, 500))
            elif price_range == "500-1000":
                price_filters.append((500, 1000))
            elif price_range == "1000-2000":
                price_filters.append((1000, 2000))
            elif price_range == "2000+":
                price_filters.append((2000, float('inf')))
        
        # Combine price range filters with OR logic
        from django.db.models import Q
        price_query = Q()
        for min_price, max_price in price_filters:
            if max_price == float('inf'):
                price_query |= Q(price__gte=min_price)
            else:
                price_query |= Q(price__gte=min_price, price__lte=max_price)
        products = products.filter(price_query)

    # Apply size filter
    if selected_sizes:
        products = products.filter(size__in=selected_sizes)

    # Apply color filter
    if selected_colors:
        products = products.filter(color__in=selected_colors)

    context = {
        'products': products,
        'categories': categories,
        'sizes': sizes,
        'colors': colors,
    }
    return render(request, 'myapp/home.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'myapp/product_detail.html', {'product': product})

def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart = request.session.get('cart', {})
        
        quantity = int(request.POST.get('quantity', 1))
        if product_id in cart:
            cart[product_id] += quantity
        else:
            cart[product_id] = quantity
        
        request.session['cart'] = cart
        request.session.modified = True
        
        return redirect('home')
    return redirect('home')

def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    # Handle POST requests (both regular and AJAX)
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')

        if quantity is not None:
            quantity = int(quantity)
            if quantity > 0:
                cart[product_id] = quantity
            else:
                cart.pop(product_id, None)  # Remove if quantity is 0 or less
            request.session['cart'] = cart
            request.session.modified = True

            # If it's an AJAX request, return JSON response
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # Recalculate total price for the response
                total_price = sum(
                    get_object_or_404(Product, id=pid).price * qty
                    for pid, qty in cart.items()
                )
                return JsonResponse({
                    'success': True,
                    'cart_item_count': sum(cart.values()),
                    'total_price': total_price,
                })

        elif 'remove' in request.POST:
            cart.pop(product_id, None)
            request.session['cart'] = cart
            request.session.modified = True
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                total_price = sum(
                    get_object_or_404(Product, id=pid).price * qty
                    for pid, qty in cart.items()
                )
                return JsonResponse({
                    'success': True,
                    'cart_item_count': sum(cart.values()),
                    'total_price': total_price,
                })

        return redirect('cart_view')

    # Build cart items list for rendering
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total_price += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'myapp/cart.html', context)

# Context processor for cart item count
def cart_context(request):
    cart = request.session.get('cart', {})
    cart_item_count = sum(cart.values())
    return {'cart_item_count': cart_item_count}

@login_required
def upload_product(request):
    message = None
    categories = Category.objects.all()

    if request.method == 'POST':
        product_id = request.POST.get('id')
        name = request.POST.get('name')
        price = request.POST.get('price')
        description = request.POST.get('description')
        quantity = request.POST.get('quantity')
        category_id = request.POST.get('category')
        images = request.FILES.getlist('images')

        try:
            category = Category.objects.get(id=category_id) if category_id else None
            product, created = Product.objects.get_or_create(
                id=product_id,
                defaults={'name': name, 'price': int(price), 'description': description, 'quantity': int(quantity), 'category': category}
            )
            if not created:
                product.name = name
                product.price = int(price)
                product.description = description
                product.quantity = int(quantity)
                product.category = category
                product.save()

            for image in images:
                ProductImage.objects.create(product=product, image=image)

            message = "產品上傳成功！"
        except Exception as e:
            message = f"錯誤：{str(e)}"

    return render(request, 'myapp/upload.html', {'message': message, 'categories': categories})

@login_required
def search_product(request):
    product = None
    message = None
    categories = Category.objects.all()

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            product = None
            message = "找不到該產品ID。"

    return render(request, 'myapp/search.html', {'product': product, 'message': message, 'categories': categories})

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    message = None

    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        description = request.POST.get('description')
        quantity = request.POST.get('quantity')
        category_id = request.POST.get('category')
        images = request.FILES.getlist('images')
        delete_images = request.POST.getlist('delete_images')

        try:
            product.name = name
            product.price = int(price)
            product.description = description
            product.quantity = int(quantity)
            product.category = Category.objects.get(id=category_id) if category_id else None
            product.save()

            for image_id in delete_images:
                image = ProductImage.objects.get(id=image_id, product=product)
                if os.path.exists(image.image.path):
                    os.remove(image.image.path)
                image.delete()

            if images:
                for image in images:
                    ProductImage.objects.create(product=product, image=image)

            message = "產品更新成功！"
        except Exception as e:
            message = f"錯誤：{str(e)}"

    return render(request, 'myapp/search.html', {'product': product, 'message': message, 'categories': categories, 'edit_mode': True})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        for image in product.images.all():
            if os.path.exists(image.image.path):
                os.remove(image.image.path)
        product.delete()
        return redirect('search_product')
    return render(request, 'myapp/search.html', {'product': product, 'delete_mode': True})

def customer_register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Customer.objects.create(
                user=user,
                name=form.cleaned_data['name'],
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data['email'],
                address=form.cleaned_data['address'],
                line_id=form.cleaned_data['line_id'],
                birthdate=form.cleaned_data['birthdate'],
            )
            login(request, user)
            return redirect('home')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'myapp/customer_register.html', {'form': form})

def customer_login(request):
    if request.method == 'POST':
        form = CustomerLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'myapp/customer_login.html', {'form': form, 'error': '無效的用戶名或密碼'})
    else:
        form = CustomerLoginForm()
    return render(request, 'myapp/customer_login.html', {'form': form})

def customer_logout(request):
    logout(request)
    return redirect('home')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('search_product')
        else:
            return render(request, 'myapp/login.html', {'error': '無效的用戶名或密碼'})
    return render(request, 'myapp/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart_view')

    products = Product.objects.filter(id__in=cart.keys())
    total_price = sum(product.price * cart[str(product.id)] for product in products)

    if request.method == 'POST':
        form = ShippingForm(request.POST)
        if form.is_valid():
            shipping_details = (
                f"Name: {form.cleaned_data['name']}\n"
                f"Phone: {form.cleaned_data['phone']}\n"
                f"Address: {form.cleaned_data['address']}"
            )

            order = Order.objects.create(
                customer=request.user.customer,
                total_price=total_price,
                shipping_address=shipping_details,
                status='Pending'
            )

            for product in products:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=cart[str(product.id)],
                    price=product.price
                )

            # Clear the cart
            request.session['cart'] = {}

            # Redirect based on payment method
            payment_method = form.cleaned_data['payment_method']
            if payment_method == 'line_pay':
                return redirect('line_pay_confirmation', order_id=order.id)
            else:
                return redirect('bank_transfer_confirmation', order_id=order.id)
    else:
        customer = request.user.customer
        initial_data = {
            'name': customer.name,
            'phone': customer.phone,
            'address': customer.address,
        }
        form = ShippingForm(initial=initial_data)

    cart_items = [
        {'product': p, 'quantity': cart[str(p.id)], 'subtotal': p.price * cart[str(p.id)]}
        for p in products
    ]
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'form': form,
    }
    return render(request, 'myapp/checkout.html', context)

@login_required
def order_confirmation(request, order_id):
    # Ensure only the customer who placed the order can view it
    order = get_object_or_404(Order, id=order_id, customer=request.user.customer)
    context = {'order': order}
    return render(request, 'myapp/order_confirmation.html', context)

@login_required
def profile(request):
    customer = request.user.customer
    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomerProfileForm(instance=customer)
    return render(request, 'myapp/profile.html', {'form': form})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'myapp/password_reset.html'
    email_template_name = 'myapp/password_reset_email.html'
    subject_template_name = 'myapp/password_reset_subject.txt'
    success_url = reverse_lazy('customer_login')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            # Check if the email exists in the database
            user = User.objects.get(email=email)
            # Send the password reset email
            form.save(
                use_https=self.request.is_secure(),
                from_email=settings.EMAIL_HOST_USER,
                request=self.request,
            )
            messages.success(self.request, '密碼重設郵件已發送至您的電子郵件地址。')
            return super().form_valid(form)
        except User.DoesNotExist:
            messages.error(self.request, '該電子郵件地址未註冊。')
            return self.form_invalid(form)

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def admin_register(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '管理員帳號創建成功！')
            return redirect('admin_register')
    else:
        form = AdminRegistrationForm()
    return render(request, 'myapp/admin_register.html', {'form': form})

@login_required
def line_pay_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user.customer)
    
    # Here you would typically:
    # 1. Generate a Line Pay QR code
    # 2. Save payment details
    # 3. Set up webhook for payment confirmation
    
    context = {
        'order': order,
    }
    return render(request, 'myapp/line_pay_confirmation.html', context)

@login_required
def bank_transfer_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user.customer)
    
    # Here you would typically:
    # 1. Set up payment status tracking
    # 2. Set up automatic order cancellation after 24 hours
    # 3. Implement payment verification system
    
    context = {
        'order': order,
    }
    return render(request, 'myapp/bank_transfer_confirmation.html', context)