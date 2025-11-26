from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Notification model.
    Used for monitoring and managing system-wide notifications.
    """
    
    # Fields displayed in the list view
    list_display = (
        'user', 
        'notification_type', 
        'is_read', 
        'is_sent',
        'created_at',
        'related_object_id',
    )
    
    # Fields that can be searched
    search_fields = (
        'user__username', 
        'message', 
        'related_object_id'
    )
    
    # Filters available on the right sidebar
    list_filter = (
        'notification_type', 
        'is_read', 
        'is_sent', 
        'created_at'
    )
    
    # Grouping and ordering of fields in the detail view
    fieldsets = (
        ('Recipient & Status', {
            'fields': (
                'user', 
                'notification_type', 
                'is_read', 
                'is_sent'
            )
        }),
        ('Content & Context', {
            'fields': (
                'message', 
                'related_object_id'
            ),
            'description': 'The related object ID refers to an Order, Product, etc.'
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 
                'read_at'
            ),
            'classes': ('collapse',), # Collapse this section by default
        }),
    )
    
    # Prevent manual modification of key fields to maintain data integrity
    readonly_fields = ('user', 'created_at', 'read_at', 'is_sent')

# Note: You generally don't need an 'admin.site.register' call 
# when using the @admin.register decorator.
