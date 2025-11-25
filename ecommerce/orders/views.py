from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated # Ensure user is logged in

# Import secure service functions and custom errors
from .services import process_order_and_deduct_inventory, InsufficientStockError 
# Import growth service for potential referral logging
# from growth.services import validate_and_log_referral 

class CheckoutAPIView(APIView):
    # Only authenticated users can access the checkout
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        # 1. Data Validation and Extraction
        # NOTE: A real project MUST use a Serializer for robust validation
        cart_data = request.data.get('items', [])
        shipping_address_data = request.data.get('shipping_address')
        referral_code = request.data.get('referral_code', None)
        
        # Get customer ID from the authenticated user
        customer_id = request.user.customer.id 

        if not cart_data or not shipping_address_data:
            return Response({"error": "Missing cart items or shipping address."}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Call the Critical Order Processing Service
        result = process_order_and_deduct_inventory(
            customer_id=customer_id, 
            cart_data=cart_data, 
            shipping_address=shipping_address_data
        )
        
        # 3. Handle Service Result
        if result.get('success'):
            order_id = result.get('order_id')

            # 4. (Optional) Log Referral if a code was used
            if referral_code:
                # This function logs the referral as 'Pending' until payment is verified
                # validate_and_log_referral(customer_id, referral_code, order_id)
                pass

            # 5. TODO: Initiate Payment Gateway (e.g., Stripe, Paymob) Call Here

            return Response({
                "message": "Order created and stock reserved successfully. Proceed to payment.", 
                "order_id": order_id
            }, status=status.HTTP_201_CREATED)

        else:
            # Return clear error to the client
            return Response({
                "error": "Order creation failed.",
                "details": result.get('error', 'Unknown internal error.')
            }, status=status.HTTP_400_BAD_REQUEST)
