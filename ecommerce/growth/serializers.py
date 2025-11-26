# File: tec/ecommerce/growth/serializers.py (English Version)

from rest_framework import serializers
from .models import (
    Referral, 
    LoyaltyPointTransaction, 
    GrowthSettings
)
from django.utils.translation import gettext_lazy as _

# ----------------------------------------------------
# 1. ReferralSerializer (For creating a new referral)
# ----------------------------------------------------
class ReferralCreateSerializer(serializers.ModelSerializer):
    """
    Serializer to handle the creation of a Referral record when a new user 
    signs up using a referral code.
    """
    # This field is required to indicate the referral code used
    referral_code = serializers.CharField(max_length=50, write_only=True)
    
    class Meta:
        model = Referral
        fields = ('referee', 'referral_code')
        # We only allow the referee to be set upon creation via the View.
        read_only_fields = ('referee',)

# ----------------------------------------------------
# 2. LoyaltyPointTransactionSerializer (For reading point logs)
# ----------------------------------------------------
class LoyaltyPointTransactionSerializer(serializers.ModelSerializer):
    
    # Converts the transaction type abbreviation to its readable display value
    transaction_type_display = serializers.CharField(
        source='get_transaction_type_display', 
        read_only=True
    )
    
    class Meta:
        model = LoyaltyPointTransaction
        fields = (
            'points_amount', 
            'transaction_type', 
            'transaction_type_display', 
            'related_order', 
            'timestamp', 
            'expiration_date'
        )
        read_only_fields = fields

# ----------------------------------------------------
# 3. LoyaltySummarySerializer (For displaying user's point summary)
# ----------------------------------------------------
class LoyaltySummarySerializer(serializers.Serializer):
    """ Non-model based Serializer to show a user's total points summary. """
    total_points = serializers.IntegerField(
        read_only=True, 
        label=_('Total Loyalty Points')
    )
    redeemable_value = serializers.DecimalField(
        max_digits=10, decimal_places=5, read_only=True, 
        label=_('Redeemable Value in Pi')
    )
