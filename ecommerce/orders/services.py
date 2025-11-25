# الملف: ecommerce/orders/services.py

# ... (Previous imports: transaction, Product, Order, OrderDetail, InsufficientStockError) ...

from django.conf import settings
import requests 
import json

# --- Placeholder/Mock Payment Service ---
def initiate_payment_request(order_id: int, total_amount: float, customer_email: str):
    """
    Sends a request to an external Payment Gateway (e.g., Stripe, Paymob)
    to generate a secure payment URL or token.
    
    NOTE: Replace this logic with your actual payment provider's API calls.
    """
    
    # 1. Fetch Payment Gateway Credentials (from settings.py)
    API_KEY = settings.PAYMENT_GATEWAY_API_KEY
    PAYMENT_URL = settings.PAYMENT_GATEWAY_URL 
    
    # 2. Prepare the payload (data to send to the payment provider)
    payload = {
        'api_key': API_KEY,
        'amount': int(total_amount * 100),  # Usually sent in cents/smallest unit
        'currency': 'USD',
        'order_reference': str(order_id),
        'customer_email': customer_email,
        'callback_url': settings.PAYMENT_SUCCESS_URL # URL the gateway sends the user back to
    }
    
    try:
        # 3. Send the request (Mocked Response for now)
        # response = requests.post(PAYMENT_URL, json=payload)
        # response.raise_for_status() # Raise error for bad status codes (4xx or 5xx)
        
        # Mocking a successful response from the payment gateway
        return {
            "success": True,
            "payment_id": f"PAY-{order_id}-{customer_email}",
            "redirect_url": f"https://payment-gateway-mock.com/pay/{order_id}"
        }

    except requests.exceptions.RequestException as e:
        # Handle connection errors or API errors
        return {"success": False, "error": f"Payment gateway request failed: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# --- 2. UPDATING process_order_and_deduct_inventory ---

def process_order_and_deduct_inventory(customer_id: int, cart_data: list, shipping_address: str, customer_email: str):
    """
    (Updated) Processes the order, reserves stock, and initiates payment request.
    """
    try:
        with transaction.atomic():
            total_order_amount = 0
            
            # 1. Create Order (and deduct stock) - (Existing Logic)
            # ... (Logic to create Order and deduct stock remains here) ...
            
            # Placeholder for total_order_amount calculated from cart
            total_order_amount = 120.50 
            
            order = Order.objects.create(
                customer_id=customer_id,
                status='PENDING', # Status remains PENDING until payment is SUCCESSFUL
                shipping_address=shipping_address,
                total_amount=total_order_amount
            )
            
            # 2. Initiate External Payment Request (New Step)
            payment_result = initiate_payment_request(
                order_id=order.id,
                total_amount=total_order_amount,
                customer_email=customer_email
            )
            
            if not payment_result['success']:
                # Raise an error to trigger ROLLBACK if payment initiation fails
                raise Exception("Failed to contact payment gateway.")

            # 3. Save the Payment ID/Token to the Order (Optional, but recommended)
            # order.payment_token = payment_result.get('payment_id')
            # order.save()

            return {
                "success": True, 
                "order_id": order.id,
                "redirect_url": payment_result['redirect_url'] # Return the URL to the client
            }

    except Exception as e:
        # This catches InsufficientStockError, DatabaseError, and Payment Initiation failure
        return {"success": False, "error": str(e)}
