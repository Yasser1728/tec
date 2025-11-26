# File: tec/ecommerce/products/views.py

from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAdminUser # Use appropriate permissions

from .models import Category, Product
from .serializers import CategorySerializer, ProductListSerializer, ProductDetailSerializer

# -----------------
# Categories ViewSet
# -----------------
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ 
    API endpoint for listing and retrieving product categories. 
    Only Read operations are allowed for public access.
    """
    queryset = Category.objects.filter(parent__isnull=True) # Only show top-level categories by default
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug' # Use slug for clean URLs (e.g., /api/products/categories/electronics/)


# -----------------
# Products ViewSet
# -----------------
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ 
    API endpoint for listing and retrieving products.
    Includes filtering, searching, and ordering.
    """
    queryset = Product.objects.filter(is_available=True, inventory_stock__gt=0).select_related('category')
    permission_classes = [AllowAny] # Publicly accessible
    lookup_field = 'slug'

    # Filter/Search/Order Backends
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # 1. Filtering by category slug
    filterset_fields = ['category__slug', 'seller']
    
    # 2. Searching by name or description
    search_fields = ['name', 'description'] 
    
    # 3. Ordering (e.g., ?ordering=price_pi or ?ordering=-created_at)
    ordering_fields = ['base_price_pi', 'rating_avg', 'created_at']
    ordering = ['name'] # Default ordering

    def get_serializer_class(self):
        """ Selects the appropriate serializer based on the action (list vs detail). """
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer # For 'retrieve' action
