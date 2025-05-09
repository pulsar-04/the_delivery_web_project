from decimal import Decimal

from django.core.mail import send_mail
from django.db import models, transaction
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
    total_bonuses = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Общо получени бонуси"
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

    def save(self, *args, **kwargs):
        is_new = self._state.adding

        # Ако поръчката вече съществува, взимаме стария статус
        if not is_new:
            old_order = Order.objects.get(pk=self.pk)
            old_status = old_order.status
        else:
            old_status = None

        # Първо записваме без да triger-ваме бонус логиката
        super().save(*args, **kwargs)

        # Проверка за бонус (само при промяна на статус на 'delivered')
        if (is_new or old_status != 'delivered') and self.status == 'delivered':
            if not hasattr(self, '_bonus_processed'):  # Критична проверка!
                with transaction.atomic():
                    delivery_person = DeliveryPerson.objects.select_for_update().get(pk=self.delivery_person_id)
                    self._check_and_apply_bonus(delivery_person)  # Подаваме delivery_person
                    self._bonus_processed = True

    def _check_and_apply_bonus(self, delivery_person):
        bonus_settings = BonusSettings.objects.filter(is_active=True).first()

        # Добавяме САМО стойността на поръчката (без бонуса)
        delivery_person.total_turnover += Decimal(str(self.total_price))

        # Проверка за бонус
        if bonus_settings and delivery_person.total_turnover >= bonus_settings.min_turnover:
            delivery_person.total_turnover += bonus_settings.bonus_amount
            delivery_person.total_bonuses += bonus_settings.bonus_amount

        delivery_person.save(update_fields=['total_turnover', 'total_bonuses'])

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


class BonusSettings(models.Model):
    min_turnover = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Минимален оборот за бонус"
    )
    bonus_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сума на бонуса"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна настройка"
    )

    class Meta:
        verbose_name = "Бонус настройка"
        verbose_name_plural = "Бонус настройки"

    def __str__(self):
        return f"Бонус: {self.bonus_amount} лв. при оборот ≥ {self.min_turnover} лв."