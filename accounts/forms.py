from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import Restaurant, Product
from django import forms
from .models import Order, OrderItem, Product

'''
class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('client', 'Клиент'),
        ('employee', 'Служител'),
        ('delivery_person', 'Доставчик'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, label='Роля')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'role')  # Добавяме полето "role"

'''
class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[
            ('client', 'Клиент'),
            ('employee', 'Служител'),
            ('delivery_person', 'Доставчик'),
        ],
        widget=forms.RadioSelect,
        required=True,
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'role')





class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'address']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['restaurant', 'name', 'description', 'price', 'category']



class OrderForm(forms.ModelForm):
    items = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Order
        fields = ['items']

class CheckoutForm(forms.Form):
    address = forms.CharField(max_length=255, required=True, label="Адрес")
    phone_number = forms.CharField(max_length=20, required=True, label="Телефонен номер")

class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        label="От дата",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        label="До дата",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
