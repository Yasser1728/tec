# File: Ecom-backend-django/core/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Admin Interface
    path('admin/', admin.site.urls),

    # ----------------------------------------------------
    # API Endpoints for the Commerce.PI Backend
    # ----------------------------------------------------
    
    # Accounts Module (User registration, login, profile management)
    # Example URL: /api/accounts/login/
    path('api/accounts/', include('accounts.urls')), 

    # Products Module (List, Detail, Search)
    # Example URL: /api/products/list/
    path('api/products/', include('products.urls')),

    # Orders Module (Checkout, Pi Escrow, Order History)
    # Example URL: /api/orders/checkout/
    path('api/orders/', include('orders.urls')),

    # Growth Module (Referral, Loyalty Points management)
    # Example URL: /api/growth/refer/
    path('api/growth/', include('growth.urls')),
    
    # Notifications Module (Push notifications, alerts)
    # path('api/notifications/', include('notifications.urls')), 
    
    # Search Module (Advanced search API)
    # path('api/search/', include('search.urls')),
]
