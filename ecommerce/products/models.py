# File: tec/ecommerce/products/models.py (Final Consolidated Version with Tags)

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings 
# from taggit.managers import TaggableManager # Optional: Use Taggit for flexibility

User = settings.AUTH_USER_MODEL

# --- New Model: Tags for flexible product classification ---
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_('Tag Name'))
    slug = models.SlugField(max_length=50, unique=True)
    
    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        
    def __str__(self):
        return self.name
# ----------------------------------------------------

class Category(models.Model):
    
    # --- Identification ---
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_('Slug')) 
    
    # --- Hierarchy ---
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='sub_categories',
        verbose_name=_('Parent Category')
    )
    description = models.TextField(blank=True, verbose_name=_('Description')) 

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        
    def __str__(self):
        return self.name

class Product(models.Model):
    
    # --- Identification & Description ---
    name = models.CharField(max_length=255, verbose_name=_('Product Name'))
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_('Slug')) 
    description = models.TextField(verbose_name=_('Full Description'))

    # --- Links & Tags ---
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, 
                                 related_name='products', verbose_name=_('Category'))
    seller = models.ForeignKey(User, on_delete=models.CASCADE, 
                               related_name='products', verbose_name=_('Seller'))
    # New Field: Flexible Tags
    tags = models.ManyToManyField(Tag, blank=True, related_name='products', verbose_name=_('Tags')) 
    # tags = TaggableManager() # Alternative if using django-taggit
    
    # --- Pricing ---
    PI_PRECISION = {'max_digits': 18, 'decimal_places': 9} 

    base_price_pi = models.DecimalField(**PI_PRECISION, verbose_name=_('Base Price (Pi)')) 
    sale_price_pi = models.DecimalField(**PI_PRECISION, null=True, blank=True, 
                                        verbose_name=_('Sale Price (Pi)')) 
    
    # --- Inventory and Status ---
    inventory_stock = models.PositiveIntegerField(default=0, verbose_name=_('Inventory Stock')) 
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, 
                                     verbose_name=_('Average Rating'))
    
    # New Status Fields
    is_available = models.BooleanField(default=True, verbose_name=_('Is Available for Purchase'))
    is_featured = models.BooleanField(default=False, verbose_name=_('Is Featured'))
    
    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Last Updated'))
    
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ('-created_at',)

    def __str__(self):
        return self.name
        
# ProductImage model (No change)
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
