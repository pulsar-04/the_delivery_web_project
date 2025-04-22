from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms
from .models import Restaurant, Product


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



class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'address']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['restaurant', 'name', 'description', 'price']


