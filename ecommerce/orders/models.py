# File: Ecom-backend-django/orders/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
# Assumed imports for User and Product models from other apps:
# from products.models import Product 
# from accounts.models import Customer 

class Order(models.Model):
    
    customer = models.ForeignKey('accounts.Customer', on_delete=models.CASCADE, verbose_name=_('Customer')) 
    
    # Updated Status Choices for Pi Escrow
    STATUS_CHOICES = [
        ('PENDING', _('Pending Payment')),
        ('PROCESSING', _('Processing/Escrow Locked')),
        ('SHIPPED', _('Shipped')),
        ('DELIVERED', _('Delivered')),
        ('COMPLETED', _('Completed/Funds Released')),
        ('CANCELED', _('Canceled')),              
        ('REFUNDED', _('Refunded')),              
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', 
                              verbose_name=_('Order Status')) 
    
    # Financial Fields (High Precision for Pi)
    total_amount_pi = models.DecimalField(max_digits=18, decimal_places=9, 
                                          verbose_name=_('Total Amount (Pi)')) 

    # Pi Escrow Fields
    pi_transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True,
                                         verbose_name=_('Pi Transaction ID'))
    escrow_release_date = models.DateTimeField(null=True, blank=True,
                                              verbose_name=_('Escrow Release Date'))
    
    # Shipping Details
    shipping_address = models.TextField(verbose_name=_('Shipping Address'))
    tracking_number = models.CharField(max_length=100, null=True, blank=True,
                                       verbose_name=_('Tracking Number'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def __str__(self):
        return f"Order #{self.id} ({self.status})"

class OrderDetail(models.Model):
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items',
                              verbose_name=_('Order'))
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT, verbose_name=_('Product')) 
    quantity = models.PositiveIntegerField(verbose_name=_('Quantity')) 
    
    # Financial Field (High Precision for Pi)
    price_at_purchase = models.DecimalField(max_digits=18, decimal_places=9, 
                                            verbose_name=_('Price at Purchase (Pi)'))
    
    class Meta:
        verbose_name = _('Order Detail')
        verbose_name_plural = _('Order Details')
        
    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Deleted Product'}"
