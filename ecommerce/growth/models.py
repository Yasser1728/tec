from django.db import models
from accounts.models import Customer
# Assuming Order model is available

class Referral(models.Model):
    referrer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='referred_by_me'
    )
    referred_customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='referred_customer'
    )
    referral_code_used = models.CharField(max_length=50)
    
    referred_order = models.ForeignKey(
        'orders.Order', on_delete=models.SET_NULL, null=True, blank=True
    )
    
    status = models.CharField(max_length=50, default='Pending')
    reward_granted_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('referrer', 'referred_customer')

class LoyaltyPointTransaction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    points_amount = models.IntegerField() 
    transaction_type = models.CharField(max_length=50) 
    
    source_order = models.ForeignKey(
        'orders.Order', on_delete=models.SET_NULL, null=True, blank=True
    ) 
    
    expiration_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
