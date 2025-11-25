from django.db import models
from django.contrib.auth.models import User # Use Django's built-in User model

class Customer(models.Model):
    # Link to the core authentication User
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    phone_number = models.CharField(max_length=15, unique=True)
    
    # Track customer's total earned loyalty points
    current_loyalty_points = models.IntegerField(default=0) 
    
    # Customer address (saved for future use)
    class CustomerAddress(models.Model):
        customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses')
        full_name = models.CharField(max_length=255)
        street_address = models.CharField(max_length=255)
        city = models.CharField(max_length=100)
        is_default = models.BooleanField(default=False)
