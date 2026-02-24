"""
URL configuration for homeproject project.
"""
from django.contrib import admin
from django.urls import path, include
from category import views as cat
from products import views as prod

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', cat.index, name='home'),
    path('list/', prod.list, name='list'),
    path('details/<int:pk>/', prod.product_details, name='details'), 
    path('cart/', prod.cart_view, name='cart_view'),
    path('add_to_cart/<int:pk>/', prod.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:pk>/', prod.remove_from_cart, name='remove_from_cart'),
    path('clear_cart/', prod.clear_cart, name='clear_cart'),
    path('accounts/', include('django.contrib.auth.urls')), 
     path('login/', prod.auth_login, name='login'),
    path('register/', prod.auth_register, name='register'),
    path('logout/', prod.auth_logout, name='logout'),
    path('checkout/', prod.checkout_view, name='checkout'),
]