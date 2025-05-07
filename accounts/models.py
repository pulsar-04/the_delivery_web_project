from decimal import Decimal

from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# Create your models here.

class User(AbstractUser):
    is_client = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)
    is_delivery_person = models.BooleanField(default=False)

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    address = models.CharField(max_length=255)
    def __str__(self):
        return self.user.username

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    department = models.CharField(max_length=100)

class DeliveryPerson(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    vehicle_type = models.CharField(max_length=50)
    total_turnover = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Общ оборот, генериран от доставчика"
    )

    def __str__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('pizza', 'Пица'),
        ('pasta', 'Паста'),
        ('salad', 'Салата'),
        ('dessert', 'Десерт'),
        ('drink', 'Напитка'),
    ]

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)  # Без дефолтна стойност

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В процес'),
        ('shipped', 'Изпратена'),
        ('delivered', 'Доставена'),
        ('cancelled', 'Отказана'),
    ]

    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, through='OrderItem')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    delivery_person = models.ForeignKey(
        'DeliveryPerson',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    address = models.CharField(max_length=255, blank=True, null=True)  # Поле за адрес
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # Поле за телефонен номер

    def __str__(self):
        return f"Поръчка #{self.id} от {self.client.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Delivery(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    delivery_person = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_delivery_person': True})
    delivery_address = models.CharField(max_length=255)
    delivery_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Доставка за поръчка #{self.order.id}"

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Потребител: {self.user.username})"

