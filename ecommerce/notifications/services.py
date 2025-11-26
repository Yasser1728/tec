# File: tec/ecommerce/notifications/services.py

from django.core.mail import send_mail
from django.conf import settings
from .models import Notification
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

# ----------------------------------------------------
# 1. Email Sender Function
# ----------------------------------------------------
def send_email_notification(recipient_email: str, subject: str, body: str):
    """ Sends an immediate email notification. """
    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False, 
        )
        return True
    except Exception as e:
        print(f"Error sending email to {recipient_email}: {e}")
        return False

# ----------------------------------------------------
# 2. Main Notification Creator and Sender
# ----------------------------------------------------
def create_and_send_notification(user: User, message: str, notification_type: str, related_id: int = None, send_email: bool = False):
    """
    Creates the notification record in the database and sends it via requested channels.
    """
    
    # 1. Create and save the notification record
    notification = Notification.objects.create(
        user=user,
        message=message,
        notification_type=notification_type,
        related_object_id=related_id,
        is_sent=False 
    )
    
    email_sent = False
    
    # 2. Send via Email (if requested and user has email)
    if send_email and user.email:
        # Assuming PROJECT_NAME is defined in settings
        project_name = getattr(settings, 'PROJECT_NAME', 'ECommerce Platform') 
        subject = f"[{notification_type} Update] - {project_name}" 
        email_sent = send_email_notification(
            recipient_email=user.email,
            subject=subject,
            body=message
        )
    
    # 3. Update the notification status
    if email_sent: 
        notification.is_sent = True
        notification.save(update_fields=['is_sent'])
        
    return notification
