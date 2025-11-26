# File: tec/ecommerce/growth/models.py (Final Consolidated Version)

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Use the custom user model defined in settings.py
User = settings.AUTH_USER_MODEL

# ----------------------------------------------------
# 1. Referral Model (Uses CustomUser)
# ----------------------------------------------------
class Referral(models.Model):
    """ Tracks user referrals. """
    
    referrer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='referred_users',
        verbose_name=_('Referrer (Inviter)')
    )
    # Changed to OneToOneField to ensure a user is only referred once
    referee = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='referred_by',
        verbose_name=_('Referee (Invited User)')
    )
    referral_code_used = models.CharField(max_length=50, blank=True, verbose_name=_('Code Used'))
    
    # Simple flag to indicate if the referrer received their reward points
    reward_granted = models.BooleanField(default=False, verbose_name=_('Reward Granted'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Referral')
        verbose_name_plural = _('Referrals')
        
    def __str__(self):
        return f"{self.referee.username} referred by {self.referrer.username if self.referrer else 'N/A'}"

# ----------------------------------------------------
# 2. Loyalty Point Transaction Model (Uses CustomUser and Order)
# ----------------------------------------------------
class LoyaltyPointTransaction(models.Model):
    """ Tracks every loyalty point movement. """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='loyalty_transactions',
        verbose_name=_('User')
    )
    points_amount = models.IntegerField(verbose_name=_('Point Amount Change'))
    
    TRANSACTION_TYPES = (
        ('EARNED_PURCHASE', _('Earned from Purchase')),
        ('EARNED_REFERRAL', _('Earned from Referral')),
        ('REDEEMED_DISCOUNT', _('Redeemed for Discount')),
        ('EXPIRED', _('Expired')),
        ('ADJUSTMENT', _('Manual Adjustment')),
    )
    transaction_type = models.CharField(
        max_length=50,
        choices=TRANSACTION_TYPES,
        verbose_name=_('Transaction Type')
    )
    related_order = models.ForeignKey(
        'orders.Order', # Assumes 'orders' app is installed
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Related Order')
    )
    
    # Crucial field retained from your model for point management
    expiration_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Expiration Date'))
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Loyalty Transaction')
        verbose_name_plural = _('Loyalty Transactions')
        ordering = ('-timestamp',)
        
    def __str__(self):
        action = "Added" if self.points_amount > 0 else "Deducted"
        return f"{self.user.username}: {action} {abs(self.points_amount)} points"

# ----------------------------------------------------
# 3. Growth Settings Model (System Constants)
# ----------------------------------------------------
class GrowthSettings(models.Model):
    """ Singleton model for storing system-wide growth constants. """
    
    points_per_pi_spent = models.DecimalField(
        max_digits=5, decimal_places=2, default=1.00,
        verbose_name=_('Points earned per 1 Pi spent')
    )
    referral_reward_points = models.IntegerField(
        default=50, 
        verbose_name=_('Points granted to Referrer for successful signup')
    )
    pi_per_point = models.DecimalField(
        max_digits=5, decimal_places=5, default=0.001,
        verbose_name=_('Pi value of 1 Loyalty Point (e.g., 0.001 Pi)')
    )
    # Days before earned points expire (for better point flow management)
    points_expiry_days = models.IntegerField(
        default=365,
        verbose_name=_('Days until points expire')
    )

    class Meta:
        verbose_name = _('Growth Setting')
        verbose_name_plural = _('Growth Settings')
        
    def save(self, *args, **kwargs):
        if self._state.adding and GrowthSettings.objects.exists():
            # Prevent creation of more than one instance
            return
        super(GrowthSettings, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        """ Retrieves the single instance, creating it if it doesn't exist. """
        if not cls.objects.exists():
            cls.objects.create()
        return cls.objects.first()

    def __str__(self):
        return "System Growth and Loyalty Settings"
