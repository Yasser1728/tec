from django.contrib import admin
from .models import Order, OrderItem, Shipment, OrderPayment # Assuming these models exist

# ----------------------------------------------------
# Order Item Inline (Items within the order)
# ----------------------------------------------------
class OrderItemInline(admin.TabularInline):
    """ Displays the products and quantities for a specific order. """
    model = OrderItem
    extra = 0 # Do not show extra blank forms by default
    readonly_fields = ('product', 'quantity', 'price_pi_at_purchase', 'line_total')
    # Prevent adding/deleting items manually in the admin for existing orders
    can_delete = False
    
    # Customize the field labels for clarity
    fieldsets = (
        (None, {
            'fields': (
                'product', 
                'quantity', 
                'price_pi_at_purchase', 
                'line_total'
            )
        }),
    )

# ----------------------------------------------------
# Order Payment Inline (Payment status)
# ----------------------------------------------------
class OrderPaymentInline(admin.StackedInline):
    """ Displays payment details for the order. """
    model = OrderPayment
    max_num = 1 # Only one payment record per order
    can_delete = False
    readonly_fields = ('transaction_id', 'payment_method', 'amount_paid_pi', 'payment_status', 'created_at')

# ----------------------------------------------------
# Main Order Admin Configuration
# ----------------------------------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """ Configuration for displaying and managing customer orders. """
    
    list_display = (
        'id', 
        'user', 
        'status', 
        'total_pi_amount', 
        'created_at', 
        'is_paid',
    )
    
    # Fields that can be searched
    search_fields = ('id', 'user__username', 'shipping_address__city')
    
    # Filters available on the right sidebar
    list_filter = ('status', 'is_paid', 'created_at')
    
    # Fields that should not be manually changed
    readonly_fields = (
        'user', 
        'total_pi_amount', 
        'created_at', 
        'updated_at',
        'is_paid',
    )
    
    # Use fieldsets to structure the detail view
    fieldsets = (
        (None, {'fields': ('user', 'status', 'total_pi_amount', 'is_paid')}),
        ('Shipping Details', {'fields': ('shipping_address', 'shipping_method')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    # Inlines for related models
    inlines = [OrderItemInline, OrderPaymentInline]


# ----------------------------------------------------
# Shipment Admin Configuration
# ----------------------------------------------------
@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    """ Configuration for managing order shipments and tracking. """
    
    list_display = (
        'order', 
        'tracking_number', 
        'carrier', 
        'status', 
        'shipped_date'
    )
    
    search_fields = ('order__id', 'tracking_number', 'carrier')
    list_filter = ('status', 'carrier')
    
    # Set the order field to be readonly as it's linked on creation
    readonly_fields = ('order', 'shipped_date')
