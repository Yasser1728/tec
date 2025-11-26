# File: Ecom-backend-django/orders/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated 
from django.db import transaction # Ensure transaction is imported for safety

# Import the core logic from the service layer
from .services import process_secure_order 
# Note: We do NOT need a separate verify/callback view for Pi's *initial* payment lock, 
# as the lock confirmation is synchronous within process_secure_order.

# --- 1. Create Order and Lock Funds (Checkout API) ---
class CheckoutPiAPIView(APIView):
    """
    Handles the checkout process: creates the order and initiates the Pi Escrow transaction.
    If the service returns success, funds have been securely locked.
    """
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        # 1. Data extraction and preparation
        user = request.user
        cart_data = request.data.get('cart_items', [])
        shipping_address = request.data.get('shipping_address')
        
        # This address is where the locked funds will eventually go.
        # MUST be sourced securely, e.g., from the Product's Seller.
        seller_pi_address = request.data.get('seller_pi_address') 

        if not cart_data or not shipping_address or not seller_pi_address:
            return Response(
                {"error": "Missing required fields.", "details": "cart_items, shipping_address, and seller_pi_address are required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 2. Call the Secure Escrow Processing Service
            # This service verifies Pi lock, deducts inventory, and creates the order atomically.
            result = process_secure_order(
                user=user, 
                cart_data=cart_data, 
                seller_pi_address=seller_pi_address
            )
            
            if result.get('success'):
                return Response({
                    "message": "Order created successfully. Pi funds are securely locked in Escrow.", 
                    "order_id": result.get('order_id'),
                    "pi_transaction_id": result.get('transaction_id')
                }, status=status.HTTP_201_CREATED)
            else:
                # If the service fails (e.g., Pi lock failed, inventory insufficient)
                return Response(
                    {"error": "Order failed during processing.", "details": result.get('message')}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            # Log the exception for debugging
            print(f"CRITICAL API ERROR: {e}") 
            return Response(
                {"error": "An internal server error occurred.", "details": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# --- 2. Order Completion/Funds Release API ---
# This is a new API needed for Pi Escrow, called when the BUYER confirms delivery.
class CompleteOrderAPIView(APIView):
    """
    Allows the authenticated user (Buyer) to manually confirm order delivery, 
    triggering the immediate release of funds from Escrow to the Seller.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        # TODO: Implement a service function (e.g., release_escrow_funds)
        # 1. Verify that the current user is the original buyer of this order.
        # 2. Call Pi SDK service to release funds immediately (pi_sdk.escrow.release_funds_to_seller(transaction_id)).
        # 3. Update Order status to 'COMPLETED'.
        
        return Response({"message": f"Order {order_id} completion initiated (Funds release pending)."}, 
                        status=status.HTTP_200_OK)
