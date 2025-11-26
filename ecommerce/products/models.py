# File: tec/ecommerce/products/models.py (Final Consolidated Version)

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings 
# Make sure your User model is set correctly in settings.AUTH_USER_MODEL

class Category(models.Model):
    
    # --- Identification ---
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_('Slug')) # ADDED: for cleaner URLs
    
    # --- Hierarchy ---
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, # Changed to SET_NULL for better data integrity
        null=True, 
        blank=True, 
        related_name='sub_categories',
        verbose_name=_('Parent Category')
    )
    description = models.TextField(blank=True, verbose_name=_('Description')) # Added: Description for context

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        
    def __str__(self):
        return self.name

class Product(models.Model):
    
    # --- Identification & Description (Using standard fields for translation layers) ---
    name = models.CharField(max_length=255, verbose_name=_('Product Name'))
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_('Slug')) # ADDED: for SEO/URLs
    description = models.TextField(verbose_name=_('Full Description'))

    # --- Links ---
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, 
                                 related_name='products', verbose_name=_('Category'))
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                               related_name='products', verbose_name=_('Seller')) # ADDED: Seller identification
    
    # --- Pricing (HIGH PRECISION FOR PI) ---
    PI_PRECISION = {'max_digits': 18, 'decimal_places': 9} # Constant for Pi currency

    base_price_pi = models.DecimalField(**PI_PRECISION, verbose_name=_('Base Price (Pi)')) # Updated for Pi
    sale_price_pi = models.DecimalField(**PI_PRECISION, null=True, blank=True, 
                                        verbose_name=_('Sale Price (Pi)')) # Updated for Pi
    
    # --- Inventory and Ratings ---
    inventory_stock = models.PositiveIntegerField(default=0, verbose_name=_('Inventory Stock')) # PositiveInteger is better
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, 
                                     verbose_name=_('Average Rating')) # Kept for display
    
    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Last Updated'))
    
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ('-created_at',)

    def __str__(self):
        return self.name
        
# ProductImage model (kept for completeness)
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', 
                                verbose_name=_('Product'))
    image = models.ImageField(upload_to='products/%Y/%m/%d', verbose_name=_('Image File'))
    is_main = models.BooleanField(default=False, verbose_name=_('Main Image'))

    class Meta:
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')
        
    def __str__(self):
        return f"Image for {self.product.name}"
