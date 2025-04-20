from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib import messages
from .models import *
from .forms import CustomUserCreationForm
from django.shortcuts import render, get_object_or_404, redirect
from .models import Restaurant, Product
from .forms import RestaurantForm, ProductForm

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            role = form.cleaned_data.get('role')
            if role == 'client':
                user.is_client = True
            elif role == 'employee':
                user.is_employee = True
            elif role == 'delivery_person':
                user.is_delivery_person = True
            user.save()
            if user.is_client:
                Client.objects.create(user=user, address='Default Address')
            messages.success(request, f'Акаунтът за {user.username} е създаден успешно!')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)  # Влизане в системата
            if user.is_client:
                return redirect('client_dashboard')  # Пренасочване към клиентския дашбоард
            elif user.is_employee:
                return redirect('employee_dashboard')  # Пренасочване към дашбоарда за служители
            elif user.is_delivery_person:
                return redirect('delivery_person_dashboard')  # Пренасочване към дашбоарда за доставчици
            else:
                return redirect('home')  # Резервен вариант, ако ролята не е зададена
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout(request):
    auth_logout(request)
    messages.success(request, 'Успешно излязохте.')
    return redirect('login')

def home(request):
    return render(request, 'accounts/home.html')

@login_required
def add_restaurant(request):
    if not request.user.is_employee:
        return redirect('home')  # Само служители могат да добавят ресторанти
    if request.method == 'POST':
        form = RestaurantForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employee_dashboard')
    else:
        form = RestaurantForm()
    return render(request, 'accounts/add_restaurant.html', {'form': form})

@login_required
def add_product(request):
    if not request.user.is_employee:
        return redirect('home')  # Само служители могат да добавят продукти
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employee_dashboard')
    else:
        form = ProductForm()
    return render(request, 'accounts/add_product.html', {'form': form})

def client_dashboard(request):
    return render(request, 'accounts/client_dashboard.html')

def employee_dashboard(request):
    return render(request, 'accounts/employee_dashboard.html')

def delivery_person_dashboard(request):
    return render(request, 'accounts/delivery_person_dashboard.html')
