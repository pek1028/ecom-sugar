from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g., "上衣", "配件"

    def __str__(self):
        return self.name

class Product(models.Model):
    SIZE_CHOICES = [
        ('xs', 'XS'),
        ('s', 'S'),
        ('m', 'M'),
        ('l', 'L'),
        ('xl', 'XL'),
    ]
    
    id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=200)
    price = models.IntegerField()  # TWD
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, blank=True)
    color = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return f"Image for {self.product.name}"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    line_id = models.CharField(max_length=100)
    birthdate = models.DateField()

    def __str__(self):
        return self.name
    
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.IntegerField(default=0)  # TWD
    status = models.CharField(max_length=20, default='Pending')  # e.g., "Pending", "Shipped", "Delivered"
    shipping_address = models.TextField()

    def __str__(self):
        return f"Order {self.id} by {self.customer.name}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.IntegerField()
    size = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"