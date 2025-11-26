# File: tec/ecommerce/accounts/models.py (Final Consolidated Version)

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# 1. Custom User Model (Must be defined if you need to extend core fields)
class CustomUser(AbstractUser):
    
    # --- Pi Network / Role Identification ---
    pi_username = models.CharField(
        max_length=150, 
        unique=True, 
        null=True, 
        blank=True, 
        verbose_name=_('Pi Network Username')
    )
    is_seller = models.BooleanField(
        default=False, 
        verbose_name=_('Is Seller')
    )
    
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    
    # Ensure to set AUTH_USER_MODEL = 'accounts.CustomUser' in settings.py!

    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        
        
# 2. User Profile Model (Stores Pi Wallet, Seller info, Loyalty Points)
class UserProfile(models.Model):
    
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='profile',
        verbose_name=_('User')
    )
    
    # --- Pi Network Specifics ---
    pi_wallet_address = models.CharField(
        max_length=100, 
        unique=True, 
        null=True, 
        blank=True, 
        verbose_name=_('Pi Wallet Address')
    )
    pi_address_verified_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name=_('Pi Address Verification Date')
    )
    
    # --- Loyalty and Customer Metrics ---
    current_loyalty_points = models.PositiveIntegerField(default=0, verbose_name=_('Loyalty Points')) # ADDED from your code

    # --- Seller Specific Details ---
    seller_name = models.CharField(max_length=255, blank=True, verbose_name=_('Store/Seller Name'))
    seller_description = models.TextField(blank=True, verbose_name=_('Seller Description'))
    seller_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
        
    def __str__(self):
        return f"Profile for {self.user.username}"


# 3. Shipping Address Model (Clean, separate model for multiple addresses)
class ShippingAddress(models.Model):
    
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='shipping_addresses',
        verbose_name=_('User')
    )
    full_name = models.CharField(max_length=255)
    street_address = models.CharField(max_length=500)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20, blank=True)
    is_default = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = _('Shipping Address')
        verbose_name_plural = _('Shipping Addresses')
        
    def __str__(self):
        return f"{self.user.username}'s address in {self.city}, {self.country}"
