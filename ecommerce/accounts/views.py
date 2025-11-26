# File: tec/ecommerce/accounts/views.py

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from .models import CustomUser, UserProfile, ShippingAddress
from .serializers import (
    RegisterSerializer, CustomUserSerializer, 
    UserProfileSerializer, ShippingAddressSerializer
)

# --- 1. Authentication (Registration & Login) ---

class RegisterAPIView(generics.CreateAPIView):
    """
    API for creating a new user account (Buyer).
    Path: /api/accounts/register/ (POST)
    """
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        """ Handles user registration and immediate JWT token generation. """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens immediately after registration
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "user": CustomUserSerializer(user, context={'request': request}).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "User registered successfully."
        }, status=status.HTTP_201_CREATED)

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    API for user login. Uses JWT (JSON Web Tokens) for authentication.
    Path: /api/accounts/login/ (POST)
    """
    # Uses the default TokenObtainPairSerializer unless customized

# --- 2. Profile Management ---

class ProfileDetailAPIView(generics.RetrieveUpdateAPIView):
    """
    API to view and update the user's profile details (UserProfile).
    Path: /api/accounts/profile/ (GET, PUT/PATCH)
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Retrieve the profile linked to the currently authenticated user
        return self.request.user.profile

# --- 3. Seller Management ---

class BecomeSellerAPIView(APIView):
    """
    API for a user to request or confirm upgrade to a Seller account.
    Path: /api/accounts/become-seller/ (POST)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        
        if user.is_seller:
            return Response({"error": "User is already registered as a seller."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # ⚠️ In a real application, this should trigger a review process.
        # For simplicity, we are setting the flag directly:
        user.is_seller = True
        user.save()
        
        # Update optional seller details on the profile
        profile = user.profile
        profile.seller_name = request.data.get('seller_name', f"{user.username}'s Store")
        profile.save()

        return Response({"message": "Account successfully upgraded to Seller status. You can now manage products."}, 
                        status=status.HTTP_200_OK)

# --- 4. Shipping Addresses ---

class ShippingAddressListCreateAPIView(generics.ListCreateAPIView):
    """
    API to list and create shipping addresses for the authenticated user.
    Path: /api/accounts/addresses/ (GET, POST)
    """
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only display addresses belonging to the current user
        return ShippingAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically link the new address to the current user
        serializer.save(user=self.request.user)
