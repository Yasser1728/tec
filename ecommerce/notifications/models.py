from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Notification(models.Model):
    
    # Notification Type Options
    TYPE_CHOICES = (
        ('ORDER', _('Order Update')),
        ('PROMOTION', _('Promotion/Sale')),
        ('ACCOUNT', _('Account Security/Update')),
        ('LOYALTY', _('Loyalty/Points')),
    )
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', 
                             verbose_name=_('Recipient User'))
    
    # Content
    message = models.TextField(verbose_name=_('Message Content'))
    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES, 
                                         verbose_name=_('Notification Type'))
    
    # Status
    is_read = models.BooleanField(default=False, verbose_name=_('Is Read'))
    is_sent = models.BooleanField(default=False, verbose_name=_('Is Sent Successfully'))
    
    # Optional Link
    related_object_id = models.IntegerField(null=True, blank=True, verbose_name=_('Related Object ID'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    read_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Read At'))

    def __str__(self):
        return f"[{self.get_notification_type_display()}] for {self.user.username}"

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ('-created_at',)
