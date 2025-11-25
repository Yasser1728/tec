from django.urls import path
from .views import CheckoutAPIView, PaymentCallbackAPIView 

urlpatterns = [
    path('checkout/', CheckoutAPIView.as_view(), name='checkout_order'),
    # Add the new path for the payment gateway webhook
    path('payment-callback/', PaymentCallbackAPIView.as_view(), name='payment_callback'), 
]
