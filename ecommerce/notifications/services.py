from accounts.models import Customer
from orders.models import Order 
# NOTE: These imports are placeholders for external libraries (e.g., Firebase, SendGrid, etc.)
# import firebase_admin.messaging as messaging 
# import smtplib
# from django.core.mail import send_mail # Django's built-in email utility

# --- Email Templates (Simple Example) ---
def get_email_template(order_status: str, order_id: int):
    """Retrieves dynamic subject and body content based on the order status."""
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

def send_push_notification(customer: Customer, title: str, body: str):
    """Placeholder function to call the Firebase Cloud Messaging (FCM) or APNS service."""
    # This assumes you have stored a device token on the Customer model (e.g., customer.device_token)
    # try:
    #     fcm_service.send_message(token=customer.device_token, title=title, body=body)
    #     return True
    # except Exception as e:
    #     # Log the error for debugging
    #     print(f"Push Failed for user {customer.id}: {e}")
    return False

def send_email_notification(recipient_email: str, subject: str, body: str):
    """Placeholder function to call the SMTP or external email service (e.g., SendGrid)."""
    # try:
    #     # Example using Django's built-in mail sender:
    #     # send_mail(subject, body, 'noreply@yourcommerce.com', [recipient_email], fail_silently=False)
    #     return True
    # except Exception as e:
    #     # Log the error
    #     print(f"Email Failed for {recipient_email}: {e}")
    return False

# --- Main Notification Dispatch Function ---
def send_order_status_update(order: Order):
    """
    Central function called when the order status changes.
    """
    customer = order.customer
    
    # --- A. Push Notification Logic ---
    push_title = f"Order Update: #{order.id}"
    push_body = f"Status changed to: {order.get_status_display()}" 
    
    send_push_notification(customer, push_title, push_body)
    
    # --- B. Email Notification Logic ---
    email_data = get_email_template(order.status, order.id)
    
    if email_data and customer.user.email:
        send_email_notification(customer.user.email, email_data['subject'], email_data['body'])
            
    return {"success": True, "status": order.status}
