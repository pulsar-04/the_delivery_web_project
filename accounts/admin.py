from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    User, Client, Employee, DeliveryPerson,
    Category, Restaurant, Product, Order, OrderItem, Delivery
)

# Регистрирайте всички модели
admin.site.register(User)
admin.site.register(Client)
admin.site.register(Employee)
admin.site.register(DeliveryPerson)
admin.site.register(Category)
admin.site.register(Restaurant)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Delivery)