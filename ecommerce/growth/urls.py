# File: tec/ecommerce/growth/urls.py (English Version)

from django.urls import path
from .views import (
    ReferralCreateAPIView,
    LoyaltySummaryAPIView,
    LoyaltyTransactionListAPIView
)

# Define the namespace for the URLs
app_name = 'growth'

urlpatterns = [
    # POST /api/growth/refer/
    # To create a new referral record (used by the referee/new customer during signup)
    path(
        'refer/', 
        ReferralCreateAPIView.as_view(), 
        name='create_referral'
    ),
    
    # GET /api/growth/loyalty/summary/
    # To get the current total loyalty points and their value
    path(
        'loyalty/summary/', 
        LoyaltySummaryAPIView.as_view(), 
        name='loyalty_summary'
    ),
    
    # GET /api/growth/loyalty/transactions/
    # To get a log of all loyalty point transactions for the user
    path(
        'loyalty/transactions/', 
        LoyaltyTransactionListAPIView.as_view(), 
        name='loyalty_transactions'
    ),
]
