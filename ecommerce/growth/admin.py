from django.contrib import admin
from .models import Referral, LoyaltyPointTransaction, GrowthSettings

# ----------------------------------------------------
# 1. Growth Settings Admin (Singleton Model)
# ----------------------------------------------------
@admin.register(GrowthSettings)
class GrowthSettingsAdmin(admin.ModelAdmin):
    """
    Admin configuration for GrowthSettings.
    Ensures only one setting object exists and displays all fields.
    """
    list_display = (
        'referral_reward_points', 
        'points_per_pi_spent', 
        'pi_per_point', 
        'points_expiry_days'
    )
    # Prevent creation of new objects and limit editing to the existing one
    def has_add_permission(self, request):
        return not GrowthSettings.objects.exists()

# ----------------------------------------------------
# 2. Referral Admin
# ----------------------------------------------------
@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    """
    Admin configuration for tracking referral events.
    """
    list_display = (
        'referrer', 
        'referee', 
        'referral_code_used', 
        'reward_granted', 
        'created_at'
    )
    
    # Fields to search by
    search_fields = ('referrer__username', 'referee__username', 'referral_code_used')
    
    # Filters
    list_filter = ('reward_granted', 'created_at')
    
    # Fields that should not be editable after creation
    readonly_fields = ('referrer', 'referee', 'referral_code_used', 'created_at')

# ----------------------------------------------------
# 3. Loyalty Point Transaction Admin
# ----------------------------------------------------
@admin.register(LoyaltyPointTransaction)
class LoyaltyPointTransactionAdmin(admin.ModelAdmin):
    """
    Admin configuration for tracking all point transactions (earned, spent, expired).
    """
    list_display = (
        'user', 
        'points_amount', 
        'transaction_type', 
        'related_order_id', 
        'created_at', 
        'expiration_date'
    )
    
    # Fields to search by
    search_fields = ('user__username', 'related_order_id')
    
    # Filters
    list_filter = ('transaction_type', 'created_at')
    
    # Make points_amount non-editable to prevent manual data corruption
    readonly_fields = ('user', 'points_amount', 'transaction_type', 'related_order_id', 'created_at')

