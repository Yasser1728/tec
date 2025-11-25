from accounts.models import Customer
from orders.models import Order 
# يجب استيراد خدمات FCM/APNS/SMTP الفعلية هنا
# import firebase_admin.messaging as messaging
# import smtplib

# --- Email Templates (Simple Example) ---
def get_email_template(order_status: str, order_id: int):
    if order_status == 'PROCESSING':
        return {
            'subject': f"Order #{order_id} Confirmed!",
            'body': "Your order has been confirmed and is being prepared for shipping."
        }
    if order_status == 'SHIPPED':
        return {
            'subject': f"Order #{order_id} is on its way!",
            'body': "Your order has shipped! Tracking number: [Tracking Number Placeholder]."
        }
    return None

# --- Main Notification Function ---
def send_order_status_update(order: Order):
    """
    Sends both Push Notification and Email based on the order's status.
    This function should be called every time order.status changes.
    """
    customer = order.customer
    
    # --- A. Push Notification Logic (Fastest method) ---
    push_title = f"Order Update: #{order.id}"
    push_body = f"Status changed to: {order.get_status_display()}" # Fetches the human-readable status
    
    # 1. Look up the customer's device token (must be stored in accounts/models.py)
    # device_token = customer.device_token 

    # 2. Call the external push service API (FCM/APNS)
    # try:
    #     message = messaging.Message(data={'status': order.status}, token=device_token)
    #     messaging.send(message)
    # except Exception as e:
    #     print(f"Failed to send push notification to {customer.id}: {e}")
    
    # --- B. Email Notification Logic ---
    email_data = get_email_template(order.status, order.id)
    
    if email_data:
        # 1. Get the customer's email address
        recipient_email = customer.user.email 
        
        # 2. Call the external email service (SMTP/SendGrid/etc.)
        # try:
        #     # smtplib.send_email(recipient_email, email_data['subject'], email_data['body'])
        # except Exception as e:
        #     print(f"Failed to send email to {recipient_email}: {e}")
            
    return {"success": True, "status": order.status}
