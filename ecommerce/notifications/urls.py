from django.urls import path
from .views import (
    NotificationListView, 
    NotificationMarkAsReadView, 
    NotificationMarkAllAsReadView
)

# Define the namespace for this app's URLs
app_name = 'notifications'

urlpatterns = [
    # 1. List and Filter Notifications
    # GET /api/notifications/
    # (Optional: ?read=false to get only unread notifications)
    path(
        '', 
        NotificationListView.as_view(), 
        name='list-notifications'
    ),
    
    # 2. Mark a Specific Notification as Read (Update)
    # PUT/PATCH /api/notifications/123/read/
    path(
        '<int:pk>/read/', 
        NotificationMarkAsReadView.as_view(), 
        name='mark-as-read'
    ),
    
    # 3. Mark All Unread Notifications as Read
    # PUT/PATCH /api/notifications/mark-all-read/
    path(
        'mark-all-read/', 
        NotificationMarkAllAsReadView.as_view(), 
        name='mark-all-as-read'
    ),
]
