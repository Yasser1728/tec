# File: tec/ecommerce/products/urls.py

from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet

# Create a router instance
router = DefaultRouter()

# Register ViewSets with the router
# This creates routes like: /products/, /products/{slug}/
router.register(r'list', ProductViewSet, basename='product') 

# This creates routes like: /categories/, /categories/{slug}/
router.register(r'categories', CategoryViewSet, basename='category')

# The router returns the list of URL patterns
urlpatterns = router.urls
