from django.db import models
from accounts.models import Customer # Import the Customer model

class Referral(models.Model):
    referrer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='referred_by_me',
        verbose_name="العميل المُحيل (المرسل)"
    )
    referred_customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='referred_customer',
        verbose_name="العميل المُحال (المستقبل)"
    )
    
    referral_code_used = models.CharField(max_length=50)
    
    # يجب ربط الإحالة بأول طلب ناجح (لتأكيد منح المكافأة)
    referred_order = models.ForeignKey(
        'orders.Order', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # حالة المكافأة: Pending, Granted, Canceled
    status = models.CharField(max_length=50, default='Pending')
    reward_granted_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "عملية إحالة"
        unique_together = ('referrer', 'referred_customer') # لضمان عدم تكرار الإحالة بين نفس العميلين
