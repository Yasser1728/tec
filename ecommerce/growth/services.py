# File: tec/ecommerce/growth/services.py (English Version)

from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import LoyaltyPointTransaction, GrowthSettings, Referral
# The Order model must be imported from the correct app (assumes 'orders')
# Ensure the correct User model is imported (User = settings.AUTH_USER_MODEL)

User = settings.AUTH_USER_MODEL # Use the custom user model
# Assume the Order model is located at 'orders.models'
# from orders.models import Order # This line must be present

# --- Constants ---
# We should rely on GrowthSettings instead of direct constants, but leaving placeholders for compatibility
# POINTS_RATE = 0.10      
# REFERRAL_BONUS = 500    

# --- Custom Error ---
class LoyaltyError(Exception):
    pass

# ----------------------------------------------------
# --- 1. Post-Purchase Points Grant Function ---
# ----------------------------------------------------
@transaction.atomic
def grant_points_on_purchase(user_id: int, order_id: int, order_total: float):
    """
    Grants loyalty points to the user based on the total order amount.
    This must be called from the orders service after a successful payment.
    """
    
    settings = GrowthSettings.load()
    points_rate = settings.points_per_pi_spent # Use the point rate from settings

    try:
        # 1. Calculate points earned (as an integer)
        # Points earned = order total * point rate (as a Decimal)
        points_earned = int(order_total * points_rate)
        
        if points_earned <= 0:
            return {"success": False, "message": "No points earned for this amount."}

        # 2. Fetch the user and calculate the expiration date
        user = get_object_or_404(User, id=user_id)
        
        # Calculate expiration date
        expiration_date = timezone.now() + timedelta(days=settings.points_expiry_days) 

        # 3. Create the transaction record
        # We don't need to update a 'current_loyalty_points' field on the User model,
        # as the total will be calculated dynamically from LoyaltyPointTransaction records.
        
        LoyaltyPointTransaction.objects.create(
            user=user,
            points_amount=points_earned,
            # Matched with the choices in our models.py: 'EARNED_PURCHASE'
            transaction_type='EARNED_PURCHASE', 
            related_order_id=order_id, 
            expiration_date=expiration_date
        )

        return {"success": True, "points_earned": points_earned}

    except Exception as e:
        # Rollback happens automatically on failure
        raise LoyaltyError(f"Failed to grant points: {str(e)}")


# ----------------------------------------------------
# --- 2. Referral Reward Grant Function ---
# ----------------------------------------------------
@transaction.atomic
def finalize_referral_reward(referee_user_id: int, order_id: int):
    """
    Validates a completed purchase by a referred user and grants rewards to the referrer.
    This must be called after the referred user's first successful purchase.
    """
    settings = GrowthSettings.load()
    reward_points = settings.referral_reward_points
    
    if reward_points <= 0:
        return {"success": False, "message": "Referral reward is disabled or set to zero."}

    # 1. Search for the pending referral record
    try:
        # Look for the Referral record matching the referee, where the reward hasn't been granted yet
        referral_record = Referral.objects.select_for_update().get(
            referee_id=referee_user_id,
            reward_granted=False,
            referrer__isnull=False # Must have a referrer
        )
    except Referral.DoesNotExist:
        # No referral record found, or reward was already granted
        return {"success": False, "error": "No pending referral found for this user."}

    # 2. Grant the reward to the referrer (Inviter)
    referrer = referral_record.referrer
    expiry_date = timezone.now() + timedelta(days=settings.points_expiry_days) 
    
    try:
        # Create a loyalty point transaction for the Referrer
        LoyaltyPointTransaction.objects.create(
            user=referrer,
            points_amount=reward_points,
            transaction_type='EARNED_REFERRAL',
            related_order_id=order_id,
            expiration_date=expiry_date
        )

        # 3. Update the referral record status
        referral_record.reward_granted = True
        referral_record.save(update_fields=['reward_granted'])
        
        # NOTE: In the model we built, the reward is granted only to the Referrer upon successful purchase.
        # If you also want to reward the Referee (the new user), another transaction must be created here.

        return {"success": True, "message": f"Referral reward granted to referrer {referrer.username}: {reward_points} points."}

    except Exception as e:
        raise LoyaltyError(f"Failed to finalize referral reward: {str(e)}")
