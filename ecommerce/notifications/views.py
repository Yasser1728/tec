# File: tec/ecommerce/notifications/views.py

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import Notification
from .serializers import NotificationSerializer

# ----------------------------------------------------
# 1. Notification List View (Fetch user's notifications)
# ----------------------------------------------------
class NotificationListView(generics.ListAPIView):
    """ Displays all notifications for the current user, with optional filtering by read status. """
    
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter notifications for the current user and order by creation time (newest first)
        queryset = Notification.objects.filter(user=self.request.user).order_by('-created_at')
        
        # Optional filtering: /api/notifications/?read=false
        is_read_filter = self.request.query_params.get('read', None)
        if is_read_filter is not None:
            if is_read_filter.lower() == 'false':
                queryset = queryset.filter(is_read=False)
            elif is_read_filter.lower() == 'true':
                queryset = queryset.filter(is_read=True)
                
        return queryset

# ----------------------------------------------------
# 2. Mark Single Notification As Read
# ----------------------------------------------------
class NotificationMarkAsReadView(generics.UpdateAPIView):
    """ Marks a specific notification as read. """
    
    queryset = Notification.objects.all()
    permission_classes = [IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Security check: Ensure the user owns the notification
        if instance.user != request.user:
            return Response({"detail": "Not authorized to access this notification."}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        # Update status if it's not already read
        if not instance.is_read:
            instance.is_read = True
            instance.read_at = timezone.now()
            instance.save(update_fields=['is_read', 'read_at'])
            
        return Response(NotificationSerializer(instance).data, status=status.HTTP_200_OK)


# ----------------------------------------------------
# 3. Mark All Notifications As Read
# ----------------------------------------------------
class NotificationMarkAllAsReadView(generics.UpdateAPIView):
    """ Marks all unread notifications for the current user as read. """
    
    permission_classes = [IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        # Bulk update all unread notifications for the current user
        updated_count = Notification.objects.filter(
            user=request.user, 
            is_read=False
        ).update(
            is_read=True, 
            read_at=timezone.now()
        )
        
        return Response({"message": f"Successfully marked {updated_count} notifications as read."}, 
                        status=status.HTTP_200_OK)
