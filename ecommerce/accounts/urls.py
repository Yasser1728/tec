# File: tec/ecommerce/accounts/urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView 
from .views import (
    RegisterAPIView, 
    CustomTokenObtainPairView, 
    ProfileDetailAPIView, 
    BecomeSellerAPIView,
    ShippingAddressListCreateAPIView
)

urlpatterns = [
    # 1. Authentication Endpoints
    # URL: /api/accounts/register/ (POST)
    path('register/', RegisterAPIView.as_view(), name='register'),
    
    # URL: /api/accounts/login/ (POST - Returns Access & Refresh Tokens)
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # URL: /api/accounts/token/refresh/ (POST - Generates new Access Token using Refresh Token)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), 

    # 2. Profile Management
    # URL: /api/accounts/profile/ (GET, PUT/PATCH)
    path('profile/', ProfileDetailAPIView.as_view(), name='profile-detail'),
    
    # 3. Seller Management
    # URL: /api/accounts/become-seller/ (POST)
    path('become-seller/', BecomeSellerAPIView.as_view(), name='become-seller'),

    # 4. Shipping Addresses
    # URL: /api/accounts/addresses/ (GET, POST)
    path('addresses/', ShippingAddressListCreateAPIView.as_view(), name='address-list-create'),
    
    # Optional: Detail/Delete/Update specific address (e.g., /api/accounts/addresses/1/)
    # path('addresses/<int:pk>/', ShippingAddressDetailAPIView.as_view(), name='address-detail'), 
]
