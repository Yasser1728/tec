from django.urls import path
from .views import ProductSearchView

# Define the namespace for this app's URLs
app_name = 'search'

urlpatterns = [
    # API endpoint for searching products: GET /api/search/products/?q=query
    path(
        'products/', 
        ProductSearchView.as_view(), 
        name='product-search'
    ),
    # You could add other search paths here if needed (e.g., searching sellers)
]
