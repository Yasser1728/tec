from django.db import models

# 1. Category Model
class Category(models.Model):
    name_en = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='sub_categories'
    )

    class Meta:
        verbose_name_plural = "Categories"

# 2. Product Model
class Product(models.Model):
    name_en = models.CharField(max_length=255)
    description_en = models.TextField()
    
    # Link to the Category
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True) 
    
    # Pricing and Sales
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Inventory and Ratings
    inventory_stock = models.IntegerField(default=0)
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    
    class Meta:
        verbose_name_plural = "Products"
