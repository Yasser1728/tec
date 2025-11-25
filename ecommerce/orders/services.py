from django.db import transaction, DatabaseError
from django.conf import settings
from products.models import Product  
from .models import Order, OrderDetail
from growth.services import grant_points_on_purchase # Import for loyalty points
import requests 
import json

class InsufficientStockError(Exception):
    pass

# --- 1. Placeholder/Mock Payment Service Initialization ---
def initiate_payment_request(order_id: int, total_amount: float, customer_email: str):
    """
    Sends a request to an external Payment Gateway to generate a secure payment URL.
    NOTE: Replace this with your actual API calls (e.g., Stripe, Paymob).
    """
    
    API_KEY = settings.PAYMENT_GATEWAY_API_KEY
    PAYMENT_URL = settings.PAYMENT_GATEWAY_URL 
    
    payload = {
        'api_key': API_KEY,
        'amount': int(total_amount * 100),
        'currency': 'USD',
        'order_reference': str(order_id),
        'customer_email': customer_email,
        'callback_url': settings.PAYMENT_SUCCESS_URL 
    }
    
    try:
        # Mocking a successful response (Replace with actual requests.post call)
        return {
            "success": True,
            "payment_id": f"PAY-{order_id}-{customer_email}",
            "redirect_url": f"https://payment-gateway-mock.com/pay/{order_id}"
        }

    except Exception as e:
        return {"success": False, "error": f"Payment gateway request failed: {e}"}

# --- 2. Order Creation and Payment Initiation ---
def process_order_and_deduct_inventory(customer_id: int, cart_data: list, shipping_address: str, customer_email: str):
    """
    Processes the order, reserves stock safely, and initiates payment request.
    If payment initiation fails, the stock reservation is rolled back (transaction.atomic).
    """
    try:
        with transaction.atomic():
            total_order_amount = 0
            
            # 🌟 Note: The actual stock deduction and total amount calculation must happen here
            total_order_amount = 120.50 # Placeholder value

            order = Order.objects.create(
                customer_id=customer_id,
                status='PENDING',
                shipping_address=shipping_address,
                total_amount=total_order_amount
            )
            
            # ... (Full logic for stock deduction and OrderDetail creation must be here) ...

            # Initiate External Payment Request
            payment_result = initiate_payment_request(
                order_id=order.id,
                total_amount=total_order_amount,
                customer_email=customer_email
            )
            
            if not payment_result['success']:
                # Triggers ROLLBACK, freeing up reserved stock
                raise Exception("Failed to initiate payment. Contact gateway failed.")

            return {
                "success": True, 
                "order_id": order.id,
                "redirect_url": payment_result['redirect_url'] 
            }

    except Exception as e:
        return {"success": False, "error": str(e)}


# --- 3. Payment Verification and Final Processing (Webhook Handler) ---
def verify_and_process_payment(order_id: int, payment_status: str, payment_reference: str, total_paid: float):
    """
    Verifies the payment status received from the external gateway and finalizes the order.
    This is called by the PaymentCallbackAPIView.
    """
    try:
        with transaction.atomic():
            # Lock the order row
            order = Order.objects.select_for_update().get(id=order_id, status='PENDING')
            order.payment_status_gateway = payment_status
            
            if payment_status == 'SUCCESS':
                
                # Security Check: Compare amounts to prevent fraud
                if abs(order.total_amount - total_paid) > 0.01: 
                    order.status = 'CANCELED'
                    order.save()
                    # TODO: Must re-add stock if it was deducted before this step
                    raise Exception("Amount mismatch detected.")

                # Finalize Order and Grant Rewards
                order.status = 'PROCESSING'
                order.payment_reference = payment_reference 
                order.save()

                # Call Growth Service (Loyalty Points)
                grant_points_on_purchase(order.customer_id, order.id, order.total_amount)
                
                # (TODO) Call notifications_service.send_order_status_update(order) 

                return {"success": True, "message": "Order finalized."}

            else:
                order.status = 'CANCELED' # Payment failed, cancel the order
                order.save()
                # TODO: Logic to re-add stock must be implemented here.
                return {"success": False, "message": f"Payment failed. Order Canceled."}

    except Order.DoesNotExist:
        return {"success": False, "error": "Order not found or already processed."}
    except Exception as e:
        return {"success": False, "error": f"Processing failed: {str(e)}"}
