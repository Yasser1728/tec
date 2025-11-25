from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from accounts.models import Customer
from .models import LoyaltyPointTransaction, Referral
from orders.models import Order # Ensure Order model is imported for source linking

# --- Constants ---
POINTS_RATE = 0.10      # 10% of order total converts to points (e.g., $100 = 10 points)
REFERRAL_BONUS = 500    # Points awarded to both parties for a successful referral

# --- Custom Error ---
class LoyaltyError(Exception):
    pass

# --- 1. Post-Purchase Points Grant Function ---
@transaction.atomic
def grant_points_on_purchase(customer_id: int, order_id: int, order_total: float):
    """
    Grants loyalty points to the customer based on the total order amount.
    This must be called from the orders service after a successful payment.
    """
    try:
        # Calculate points earned (as an integer)
        points_earned = int(order_total * POINTS_RATE)
        
        if points_earned <= 0:
            return {"success": False, "message": "No points earned for this amount."}

        # 1. Update the customer's total balance
        # Use select_for_update() for transaction safety
        customer = Customer.objects.select_for_update().get(id=customer_id) 
        customer.current_loyalty_points += points_earned
        customer.save()

        # 2. Create the transaction record
        LoyaltyPointTransaction.objects.create(
            customer=customer,
            points_amount=points_earned,
            transaction_type='PURCHASE',
            source_order_id=order_id,
            # Example expiration: 1-year expiration
            expiration_date=timezone.now() + timedelta(days=365) 
        )

        return {"success": True, "points_earned": points_earned}

    except Customer.DoesNotExist:
        return {"success": False, "error": "Customer not found."}
    except Exception as e:
        # Rollback happens automatically on failure
        return {"success": False, "error": f"Failed to grant points: {str(e)}"}

# --- 2. Referral Reward Grant Function ---
@transaction.atomic
def finalize_referral_reward(referred_customer_id: int, referred_order_id: int):
    """
    Validates a completed purchase by a referred customer and grants rewards to both parties.
    This must be called after the referred customer's first successful purchase.
    """
    try:
        # 1. Search for the pending referral record
        referral_record = Referral.objects.select_for_update().get(
            referred_customer_id=referred_customer_id,
            status='Pending'
        )

        # 2. Grant the reward to the referrer (sender)
        referrer = referral_record.referrer
        referrer.current_loyalty_points += REFERRAL_BONUS
        referrer.save()
        
        # 3. Grant the reward to the referred customer (receiver)
        referred_customer = referral_record.referred_customer
        referred_customer.current_loyalty_points += REFERRAL_BONUS
        referred_customer.save()

        # 4. Update the referral record status
        referral_record.status = 'GRANTED'
        referral_record.referred_order_id = referred_order_id
        referral_record.reward_granted_date = timezone.now()
        referral_record.save()
        
        # NOTE: You should also create LoyaltyPointTransaction records here for clean history.

        return {"success": True, "message": f"Referral reward granted to both parties: {REFERRAL_BONUS} points each."}

    except Referral.DoesNotExist:
        return {"success": False, "error": "No pending referral found for this customer."}
    except Exception as e:
        return {"success": False, "error": f"Failed to finalize referral: {str(e)}"}
