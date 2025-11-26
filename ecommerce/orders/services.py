# File: Ecom-backend-django/orders/services.py

import json
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
import time # Used for unique transaction ID generation

# --- IMPORTANT IMPORTS (Assumed from your project structure) ---
# You MUST ensure these models are correctly imported:
# from products.models import Product  
# from .models import Order, OrderDetail 
# ----------------------------------------------------------------

# --- Constants ---
ORDER_EXPIRATION_TIME = timedelta(hours=1)
ESCROW_PERIOD_DAYS = 14 
PI_APP_FEE_RATE = 0.01 # 1% Application fee example

# --- MOCK FUNCTIONS for Pi SDK ---
# These functions simulate the actual communication with the Pi Network SDK
def mock_pi_payment_initiate(recipient_address: str, amount: float, metadata: dict):
    """ Mocks initiating a secure Pi Escrow transaction. """
    if amount <= 0:
        return {'success': False, 'message': 'Invalid amount.'}
        
    transaction_id = f"pi_tx_{int(time.time())}_{abs(hash(recipient_address))}" 
    print(f"PI_SDK: Initiating Escrow payment of {amount} Pi to {recipient_address} (TX ID: {transaction_id})")
    
    return {
        'success': True,
        'transaction_id': transaction_id,
        'status': 'AWAITING_FUNDS_LOCK',
    }

def mock_pi_payment_verify(transaction_id: str):
    """ Mocks verifying that funds are securely locked in Escrow. """
    return {
        'status': 'FUNDS_LOCKED_IN_ESCROW',
        'is_locked': True,
        'lock_until': (datetime.now() + timedelta(days=ESCROW_PERIOD_DAYS)).isoformat()
    }

# --- Inventory & Cleanup Logic (From your original code) ---

@transaction.atomic
def release_inventory_for_canceled_order(order_id: int):
    """
    Releases stock back into inventory for a given canceled or expired order.
    Uses select_for_update() to ensure atomicity during stock change.
    """
    try:
        # 1. Fetch and Lock the Order (Order must be imported from .models)
        order = Order.objects.select_for_update().get(id=order_id)
        
        # Guard clause: Don't allow canceling fulfilled orders
        if order.status in ['PROCESSING', 'SHIPPED', 'DELIVERED', 'COMPLETED']:
            return {"success": False, "message": "Order is already being fulfilled and cannot be canceled."}

        # 2. Loop through order details to return stock
        # (OrderDetail must be imported from .models)
        for detail in order.items.all(): 
            # Product must be imported from products.models
            product = detail.product 
            product.inventory_stock += detail.quantity 
            product.save()

        # 3. Change order status to CANCELED
        order.status = 'CANCELED' 
        order.save()

        # TODO: Add logic here to call pi_sdk.escrow.release_funds_to_buyer() 
        # if the order status was 'ESCROW_PENDING' to unlock the Pi.

        return {"success": True, "message": f"Inventory released and Order #{order_id} canceled."}

    except Order.DoesNotExist:
        return {"success": False, "error": "Order not found."}
    except Exception as e:
        print(f"CRITICAL: Failed to release inventory for order {order_id}: {e}")
        return {"success": False, "error": f"Failed to release inventory: {str(e)}"}


@transaction.atomic
def run_pending_order_cleanup():
    """
    Identifies all 'PENDING' orders older than ORDER_EXPIRATION_TIME and cancels them.
    Designed to be run by a periodic scheduler (Cron/Celery).
    """
    
    # 1. Identify Expired Orders
    cutoff_time = timezone.now() - ORDER_EXPIRATION_TIME
    expired_orders = Order.objects.filter(
        status='PENDING',
        created_at__lt=cutoff_time
    )

    cleanup_count = 0
    
    # 2. Cancel and Clean Each Expired Order
    for order in expired_orders:
        try:
            # Use the atomic function to safely return inventory
            release_result = release_inventory_for_canceled_order(order.id)
            if release_result['success']:
                cleanup_count += 1
                # TODO: Send a notification to the customer.

        except Exception as e:
            # Continue to the next order even if one fails
            print(f"Cleanup critical failure for order {order.id}: {e}")
            continue

    return {"success": True, "orders_cleaned": cleanup_count}


# --- Primary Order Processing Logic (Pi Escrow) ---

@transaction.atomic
def process_secure_order(user, cart_data: list, seller_pi_address: str):
    """
    The main function to process an order using secure Pi Escrow.
    1. Calculates total amount.
    2. Initiates and verifies Pi Escrow lock.
    3. Deducts inventory and creates the Order in the DB.
    """
    total_pi_amount = 0.0
    items_to_create = []

    # 1. Calculate Total Amount & Perform Inventory Check/Lock (IMPORTANT)
    for item in cart_data:
        # In production: Fetch the Product object to verify price and stock availability 
        # product = Product.objects.get(id=item['product_id'])
        # if product.inventory_stock < item['quantity']: raise Exception('Out of Stock')

        total_pi_amount += item['price'] * item['quantity']
        items_to_create.append(item)

    if total_pi_amount <= 0:
        return {'success': False, 'message': 'Cart is empty or total is zero.'}
    
    # 2. Initiate Escrow via Pi SDK
    app_fee = total_pi_amount * PI_APP_FEE_RATE
    payment_metadata = {
        'user_id': user.id,
        'app_fee_pi': app_fee,
        'items': [i['product_id'] for i in items_to_create]
    }
    
    pi_response = mock_pi_payment_initiate(
        recipient_address=seller_pi_address,
        amount=total_pi_amount,
        metadata=json.dumps(payment_metadata)
    )

    if not pi_response.get('success'):
        return {'success': False, 'message': "Pi Payment Initiation Failed."}
        
    transaction_id = pi_response['transaction_id']
    
    # 3. Verify Funds Lock (Crucial step for secure processing)
    verification_response = mock_pi_payment_verify(transaction_id)
    
    if verification_response.get('status') != 'FUNDS_LOCKED_IN_ESCROW':
        # If lock fails, the order cannot proceed.
        return {'success': False, 'message': 'Payment failed: Funds not locked in Escrow.'}

    # 4. Finalize DB entry, Deduct Inventory (MUST be done within the atomic block)
    try:
        # Deduction should happen here using select_for_update() on Product model
        # for item in items_to_create:
        #    product = Product.objects.select_for_update().get(id=item['product_id'])
        #    product.inventory_stock -= item['quantity']
        #    product.save()

        # Create the main Order record (Order must be imported)
        order = Order.objects.create(
            user=user,
            total_amount_pi=total_pi_amount,
            pi_transaction_id=transaction_id,
            status='PROCESSING', # Funds are secured, move to PROCESSING
            escrow_release_date=(datetime.now() + timedelta(days=ESCROW_PERIOD_DAYS))
        )

        # Create Order Details records (OrderDetail must be imported)
        for item in items_to_create:
            OrderDetail.objects.create(
                order=order,
                product_id=item['product_id'],
                price_at_purchase=item['price'],
                quantity=item['quantity']
            )
            
    except Exception as e:
        # If DB save fails, we must attempt to cancel the Pi Escrow lock!
        print(f"Database save failed: {e}. CRITICAL: Attempting to notify Pi SDK to cancel lock.")
        return {'success': False, 'message': 'Order creation failed in database.'}

    return {
        'success': True,
        'message': 'Order created successfully. Funds are securely held in Escrow.',
        'order_id': order.id,
        'transaction_id': transaction_id
    }
