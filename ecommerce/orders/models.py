from django.db import models
from products.models import Product # Assuming Product model is imported correctly

# 1. Order Model
class Order(models.Model):
    # Assuming Customer model exists in accounts.models
    # customer = models.ForeignKey('accounts.Customer', on_delete=models.CASCADE) 
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELED', 'Canceled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING') 
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Orders"

# 2. Order Detail Model (Items within an order)
class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT) 
    
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name_plural = "Order Details"
