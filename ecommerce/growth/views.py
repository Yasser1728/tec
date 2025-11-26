from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .models import Referral, LoyaltyPointTransaction, GrowthSettings
from .serializers import (
    ReferralCreateSerializer, 
    LoyaltyPointTransactionSerializer, 
    LoyaltySummarySerializer
)

User = get_user_model()

# ----------------------------------------------------
# 1. API View for Referral Signup (POST)
# ----------------------------------------------------
class ReferralCreateAPIView(generics.CreateAPIView):
    """
    Handles the creation of a Referral record when a new user (Referee) 
    uses a referral code during sign-up/onboarding.

    The user making the request (request.user) is the new Referee.
    Requires authentication (IsAuthenticated) to ensure the Referee is logged in.
    """
    serializer_class = ReferralCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        referral_code_used = serializer.validated_data.get('referral_code')
        
        # 1. Find the Referrer (the user whose code was used)
        try:
            # Assumes the referral code is the referrer's username or a related field 
            # (e.g., in a custom user model or a separate Profile model).
            # We will assume here the code is the Referrer's username for simplicity.
            referrer = User.objects.get(username__iexact=referral_code_used)
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid referral code or referrer not found."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. Check if the current user (referee) has already been referred
        if Referral.objects.filter(referee=request.user).exists():
            return Response(
                {"detail": "This user has already been marked as referred."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Prevent self-referral
        if referrer == request.user:
            return Response(
                {"detail": "You cannot refer yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4. Create the Referral record
        Referral.objects.create(
            referrer=referrer,
            referee=request.user,
            referral_code_used=referral_code_used
        )
        
        # Note: The reward granting logic runs automatically via the signals.py file.
        
        return Response(
            {"detail": "Referral recorded successfully. Reward processing initiated."},
            status=status.HTTP_201_CREATED
        )

# ----------------------------------------------------
# 2. API View for User's Loyalty Point Summary (GET)
# ----------------------------------------------------
class LoyaltySummaryAPIView(APIView):
    """
    Returns the total available loyalty points and their redeemable value for the current user.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Calculate the total non-expired points
        # Sum the points_amount for all transactions that have not expired yet
        total_points = LoyaltyPointTransaction.objects.filter(
            user=user,
            expiration_date__gt=timezone.now() # Only count non-expired points
        ).aggregate(Sum('points_amount'))['points_amount__sum'] or 0
        
        # Load growth settings
        settings = GrowthSettings.load()
        
        # Calculate the redeemable value in Pi
        redeemable_value = total_points * settings.pi_per_point
        
        # Serialize the summary data
        data = {
            'total_points': total_points,
            'redeemable_value': redeemable_value
        }
        
        serializer = LoyaltySummarySerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ----------------------------------------------------
# 3. API View for User's Loyalty Point Transactions (GET)
# ----------------------------------------------------
class LoyaltyTransactionListAPIView(generics.ListAPIView):
    """
    Lists all loyalty point transactions for the currently authenticated user.
    """
    serializer_class = LoyaltyPointTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Return transactions for the logged-in user only
        return LoyaltyPointTransaction.objects.filter(user=self.request.user)

