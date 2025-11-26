# File: tec/ecommerce/search/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from haystack.query import SearchQuerySet
from .serializers import SearchResultSerializer
from rest_framework import status
# Import the Product model to ensure results are filtered correctly
from tec.ecommerce.products.models import Product 

# ----------------------------------------------------
# Main Search API View
# ----------------------------------------------------
class ProductSearchView(APIView):
    """
    Handles search requests for products and returns results from the search engine.
    Endpoint: /api/search/products/?q=query
    """
    # Permissions can be set to allow unauthenticated users to search
    # permission_classes = [AllowAny] 
    
    def get(self, request, format=None):
        query = request.query_params.get('q', None)
        
        if not query:
            # Return a bad request status or simply an empty list if no query is provided
            return Response({"results": []}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Execute the search using Haystack
        # .filter(content=query) searches the main 'text' field
        # .models(Product) ensures we only get product results
        # .load_all() pre-fetches the Django objects for serialization efficiency
        sqs = SearchQuerySet().filter(content=query).models(Product).load_all()

        # Optional: Add simple category filtering from URL parameters
        category_filter = request.query_params.get('category', None)
        if category_filter:
             # Assumes the category filter is indexed in indexes.py
             sqs = sqs.filter(category_name=category_filter) 
        
        # 2. Serialize the results
        # Use context to pass request information to nested serializers
        context = {'request': request}
        serializer = SearchResultSerializer(sqs, many=True, context=context)
        
        # 3. Return the response
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)
