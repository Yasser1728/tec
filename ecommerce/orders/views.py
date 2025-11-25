from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated 
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .services import process_order_and_deduct_inventory, verify_and_process_payment 
# from growth.services import validate_and_log_referral 

# --- A. Checkout API ---
class CheckoutAPIView(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        # 1. Data extraction and validation
        customer_id = request.user.customer.id
        customer_email = request.user.email # Used for payment gateway

        result = process_order_and_deduct_inventory(
            customer_id=customer_id, 
            cart_data=request.data.get('items', []), 
            shipping_address=request.data.get('shipping_address'),
            customer_email=customer_email
        )
        
        if result.get('success'):
            return Response({
                "message": "Order created. Redirecting for payment.", 
                "order_id": result.get('order_id'),
                "redirect_url": result.get('redirect_url') # Returns payment link to client
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Failed to create order.", "details": result.get('error')}, status=status.HTTP_400_BAD_REQUEST)

# --- B. Payment Callback API (New Webhook) ---
@method_decorator(csrf_exempt, name='dispatch')
class PaymentCallbackAPIView(APIView):
    """
    Receives the payment status webhook/callback from the external payment gateway.
    """
    def post(self, request):
        
        data = request.data
        
        try:
            # 🌟 Keys depend entirely on your payment provider (e.g., Paymob, Stripe)
            order_id = int(data.get('order_ref'))
            payment_status = data.get('payment_status') # Should be "SUCCESS" or "FAILED"
            payment_reference = data.get('txn_id')
            total_paid = float(data.get('amount_paid')) 
            
            result = verify_and_process_payment(
                order_id=order_id,
                payment_status=payment_status,
                payment_reference=payment_reference,
                total_paid=total_paid
            )
            
            if result['success']:
                # Return 200 OK status to the payment gateway (Critical!)
                return Response({"message": "Verification successful."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Verification failed.", "details": result['error']}, status=status.HTTP_200_OK)

        except Exception as e:
            # Return 500 only if truly necessary, often 200 OK is safer to prevent endless retries
            return Response({"error": "Internal processing error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
