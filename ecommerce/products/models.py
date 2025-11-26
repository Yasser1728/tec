from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
# Assuming Product and User models are defined and imported in the main file scope

# --- Product Review Model ---
class ProductReview(models.Model):
    """ Stores user ratings and comments for a specific product. """
    
    # Relationships (Assuming 'Product' and 'User' are defined above this class)
    product = models.ForeignKey(
        'Product', # Use string reference if Product model is defined later in the file
        on_delete=models.CASCADE, 
        related_name='reviews', 
        verbose_name=_('Product')
    )
    user = models.ForeignKey(
        'User', # Use string reference if User model is defined elsewhere or via settings.AUTH_USER_MODEL
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='submitted_reviews', 
        verbose_name=_('User')
    )
    
    # Rating field (1 to 5 stars)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Rating (1-5 stars)')
    )
    
    comment = models.TextField(blank=True, verbose_name=_('Review Comment'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    class Meta:
        verbose_name = _('Product Review')
        verbose_name_plural = _('Product Reviews')
        ordering = ('-created_at',)
        # Ensures a user can only submit one review per product
        unique_together = ('product', 'user')
        
    def __str__(self):
        # Requires the Product model to have a 'name' attribute
        return f"{self.rating} stars for {self.product.name} by {self.user.username}"
