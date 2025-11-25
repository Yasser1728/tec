# File: ecommerce/orders/services.py

# ... (Previous imports: transaction, Order, OrderDetail, etc.) ...
from django.utils import timezone
from datetime import timedelta
# Ensure the following are imported:
# from django.db import transaction
# from .models import Order, OrderDetail
# from products.models import Product 

# --- Constants ---
# Order validity limit: 1 hour (Orders older than this in PENDING status are canceled)
ORDER_EXPIRATION_TIME = timedelta(hours=1) 

@transaction.atomic
def release_inventory_for_canceled_order(order_id: int):
    """
    Releases stock back into inventory for a given canceled or pending order.
    """
    try:
        # 1. Fetch and Lock the Order
        order = Order.objects.select_for_update().get(id=order_id)
        
        # Don't touch orders that are already processing/shipped
        if order.status in ['PROCESSING', 'SHIPPED', 'DELIVERED']:
            return {"success": False, "message": "Order is already being fulfilled and cannot be canceled."}

        # 2. Loop through order details to return stock
        for detail in order.items.all():
            product = detail.product
            # Ensure the deduction logic is reversed here:
            product.inventory_stock += detail.quantity 
            product.save()

        # 3. Change order status to CANCELED
        order.status = 'CANCELED' 
        order.save()

        return {"success": True, "message": f"Inventory released and Order #{order_id} canceled."}

    except Order.DoesNotExist:
        return {"success": False, "error": "Order not found."}
    except Exception as e:
        # Log this critical failure
        print(f"CRITICAL: Failed to release inventory for order {order_id}: {e}")
        return {"success": False, "error": f"Failed to release inventory: {str(e)}"}


@transaction.atomic
def run_pending_order_cleanup():
    """
    Identifies all 'PENDING' orders older than ORDER_EXPIRATION_TIME and cancels them.
    This function should be run by a periodic scheduler (e.g., a Cron Job).
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
                # TODO: Send a notification to the customer: "Your order was canceled due to non-payment."

        except Exception as e:
            # Continue to the next order even if one fails
            print(f"Cleanup critical failure for order {order.id}: {e}")
            continue

    return {"success": True, "orders_cleaned": cleanup_count}
