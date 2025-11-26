from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer 
from django.utils.translation import gettext_lazy as _
# Assuming these models exist in .models:
from .models import UserProfile, UserAddress, CustomUser 

User = get_user_model() 

# NOTE: Using UserAddress for consistency, but if your model is ShippingAddress, 
# replace all instances of UserAddress with ShippingAddress.
ShippingAddress = UserAddress 

# ----------------------------------------------------
# 1. Registration Serializer (Sign-Up)
# ----------------------------------------------------
class RegisterSerializer(serializers.ModelSerializer):
    """ Handles user creation and links a UserProfile automatically. """
    
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        # Fields based on your consolidated list
        fields = ('username', 'email', 'pi_username', 'password', 'password2', 'first_name', 'last_name')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True}
        }

    def validate(self, attrs):
        """ Checks password match, length, and email uniqueness. """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": _("Password fields didn't match.")})
        
        if len(attrs['password']) < 8:
            raise serializers.ValidationError({"password": _("Password must be at least 8 characters long.")})
            
        # Ensure email is unique (crucial check)
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": _("A user with this email already exists.")})
            
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """ Creates CustomUser and automatically generates a linked UserProfile. """
        validated_data.pop('password2') 
        
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            pi_username=validated_data.get('pi_username'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        # Automatic creation of UserProfile is handled here for reliability
        UserProfile.objects.create(user=user)
        
        return user

# ----------------------------------------------------
# 2. Custom JWT Token Serializer (Login / Authentication)
# ----------------------------------------------------
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """ 
    Customizes the JWT login response to include essential user details. 
    This is required for token-based login.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims to the token payload (lightweight data)
        token['username'] = user.username
        token['is_seller'] = user.is_seller
        
        return token

    def validate(self, attrs):
        # Default validation (checks credentials) and returns 'access' and 'refresh' tokens
        data = super().validate(attrs)

        # Add User Information to the response body (not the token payload)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'is_seller': self.user.is_seller,
            'is_verified': self.user.is_verified,
        }
        
        return data

# ----------------------------------------------------
# 3. User Profile Serializer (Used internally for nesting)
# ----------------------------------------------------
class UserProfileSerializer(serializers.ModelSerializer):
    """ Serializer for the UserProfile model. """
    
    class Meta:
        model = UserProfile
        exclude = ('id', 'user') 
        # Fields that shouldn't be manually updated by the user
        read_only_fields = ('seller_rating', 'current_loyalty_points', 'pi_address_verified_at', 'referral_code')

# ----------------------------------------------------
# 4. User Detail Serializer (For /api/accounts/me - GET/PUT/PATCH)
# ----------------------------------------------------
class CustomUserSerializer(serializers.ModelSerializer):
    """ Serializer for the CustomUser model, nested with UserProfile and Addresses. """
    
    # Nested serializer for profile details (read/write)
    profile = UserProfileSerializer(required=False) 
    
    # Nested serializer for addresses (read-only for listing)
    addresses = serializers.SerializerMethodField() # We'll use a method to handle the custom name

    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'is_seller', 'pi_username', 'profile', 'addresses'
        )
        read_only_fields = ('id', 'is_seller', 'pi_username')

    def get_addresses(self, obj):
        # Dynamically use the correct address serializer based on your model name
        if hasattr(obj, 'shippingaddress_set'):
            return ShippingAddressSerializer(obj.shippingaddress_set.all(), many=True).data
        # Fallback if using the previous model name 'addresses'
        return ShippingAddressSerializer(obj.addresses.all(), many=True).data

    @transaction.atomic
    def update(self, instance, validated_data):
        """ Handles updating both CustomUser fields and nested UserProfile fields. """
        
        # Handle nested profile update
        profile_data = validated_data.pop('profile', {})
        if profile_data:
            profile_instance = instance.profile
            profile_serializer = UserProfileSerializer(
                profile_instance, 
                data=profile_data, 
                partial=True,
                context=self.context
            )
            if profile_serializer.is_valid(raise_exception=True):
                profile_serializer.save()

        # Handle CustomUser model update
        return super().update(instance, validated_data)


# ----------------------------------------------------
# 5. Shipping Address Serializer (For CRUD operations)
# ----------------------------------------------------
class ShippingAddressSerializer(serializers.ModelSerializer):
    """ Serializer for the ShippingAddress model (or UserAddress). """
    
    class Meta:
        model = ShippingAddress
        # Exclude 'user' field, as it is set automatically by the view (current user)
        exclude = ('user',) 
