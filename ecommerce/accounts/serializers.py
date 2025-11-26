# File: tec/ecommerce/accounts/serializers.py

from rest_framework import serializers
from django.db import transaction
from .models import CustomUser, UserProfile, ShippingAddress

# ----------------------------------------------------
# 1. Registration Serializer 
# Used for creating a new CustomUser and linking a UserProfile
# ----------------------------------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'pi_username', 'password', 'password2', 'first_name', 'last_name')
        extra_kwargs = {'email': {'required': True}}

    def validate(self, attrs):
        # Validation 1: Check if passwords match
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        # Validation 2: Check password length
        if len(attrs['password']) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long."})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        # Pop password2 as it's not a model field
        validated_data.pop('password2') 
        
        # Create CustomUser
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            pi_username=validated_data.get('pi_username'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        # Automatically create a UserProfile for the new user
        UserProfile.objects.create(user=user)
        
        return user


# ----------------------------------------------------
# 2. User Profile Serializers (for GET and PUT/PATCH requests)
# ----------------------------------------------------
class UserProfileSerializer(serializers.ModelSerializer):
    """ Serializer for the UserProfile model. """
    
    class Meta:
        model = UserProfile
        exclude = ('id', 'user') 
        # Fields that shouldn't be manually updated by the user
        read_only_fields = ('seller_rating', 'current_loyalty_points', 'pi_address_verified_at')

class CustomUserSerializer(serializers.ModelSerializer):
    """ Serializer for the CustomUser model, nested with UserProfile. """
    
    # Nested serializer to display profile data when fetching user details
    profile = UserProfileSerializer(read_only=True) 

    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'is_seller', 'pi_username', 'profile'
        )
        # These fields are generally set by the system or during specific processes
        read_only_fields = ('id', 'is_seller', 'pi_username')


# ----------------------------------------------------
# 3. Shipping Address Serializer
# ----------------------------------------------------
class ShippingAddressSerializer(serializers.ModelSerializer):
    """ Serializer for the ShippingAddress model. """
    
    class Meta:
        model = ShippingAddress
        exclude = ('user',) # User field is set automatically by the view
