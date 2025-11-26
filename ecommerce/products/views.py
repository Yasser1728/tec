# File: tec/ecommerce/products/views.py (Completed)

from rest_framework import viewsets, filters, generics # <-- Added generics here
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAdminUser 
from django.db.models import Q # <-- Added Q for complex lookups

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
    queryset = Category.objects.filter(parent__isnull=True) 
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug' 


# -----------------
# Products ViewSet
# -----------------
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ 
    API endpoint for listing and retrieving products.
    Includes filtering, searching, and ordering.
    """
    queryset = Product.objects.filter(is_available=True, inventory_stock__gt=0).select_related('category')
    permission_classes = [AllowAny] 

    # Filter/Search/Order Backends
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # 1. Filtering by category slug
    filterset_fields = ['category__slug', 'seller']
    
    # 2. Searching by name or description
    search_fields = ['name', 'description'] 
    
    # 3. Ordering (e.g., ?ordering=price_pi or ?ordering=-created_at)
    ordering_fields = ['base_price_pi', 'rating_avg', 'created_at']
    ordering = ['name'] 

    def get_serializer_class(self):
        """ Selects the appropriate serializer based on the action (list vs detail). """
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer 
        
# -----------------
# Custom Search API View (Needed for the updated urls.py)
# -----------------
class ProductSearchAPIView(generics.ListAPIView):
    """
    Custom API endpoint for searching products using a 'q' query parameter.
    Performs search across name, description, and keywords.
    """
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True, inventory_stock__gt=0)
        query = self.request.query_params.get('q', None)
        
        if query:
            # Perform a case-insensitive search across multiple fields (name, description, tags)
            queryset = queryset.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) |
                Q(tags__name__icontains=query) # Assumes you have a ManyToMany field 'tags'
            ).distinct() 
            
        return queryset.select_related('category') # Optimize lookup

