from django.urls import path
from .views import CheckoutAPIView, OrderHistoryAPIView # Assuming OrderHistory exists

urlpatterns = [
    # API Path: /api/v1/orders/checkout/
    path('checkout/', CheckoutAPIView.as_view(), name='checkout_order'),
    
    # API Path: /api/v1/orders/history/
    # path('history/', OrderHistoryAPIView.as_view(), name='order_history'),
]
