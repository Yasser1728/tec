# File: tec/ecommerce/notifications/serializers.py

from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    """ Serializer for presenting notifications to the user. """
    
    # Read-only field displaying the human-readable notification type
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 
            'message', 
            'notification_type',
            'notification_type_display',
            'is_read', 
            'created_at',
            'read_at',
            'related_object_id'
        ]
        read_only_fields = fields 
