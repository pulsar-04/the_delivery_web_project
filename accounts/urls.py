from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('add-restaurant/', views.add_restaurant, name='add_restaurant'),
    path('add-product/', views.add_product, name='add_product'),
    path('client-dashboard/', views.client_dashboard, name='client_dashboard'),
    path('employee-dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('delivery-person-dashboard/', views.delivery_person_dashboard, name='delivery_person_dashboard'),
    path('add-restaurant/', views.add_restaurant, name='add_restaurant'),
    path('edit-restaurant/<int:pk>/', views.edit_restaurant, name='edit_restaurant'),
    path('delete-restaurant/<int:pk>/', views.delete_restaurant, name='delete_restaurant'),
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:pk>/', views.delete_product, name='delete_product'),
]