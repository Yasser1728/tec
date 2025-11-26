# File: tec/ecommerce/search/serializers.py

from rest_framework import serializers
# Note: SearchResult is typically available if Haystack is installed
from haystack.models import SearchResult 

class SearchResultSerializer(serializers.Serializer):
    """ 
    Serializer to handle SearchResult objects returned by Haystack.
    """
    # Metadata fields from the search engine
    model_name = serializers.CharField(source='model_name')
    pk = serializers.IntegerField()
    score = serializers.FloatField()
    highlighted = serializers.CharField(required=False, allow_blank=True)
    
    # Custom field to include the full object details
    data = serializers.SerializerMethodField()

    def get_data(self, instance):
        """ Dynamically load the full model object based on model_name. """
        
        # Load the actual ProductSerializer from the products app
        if instance.model_name == 'product':
            # IMPORTANT: Ensure this serializer exists in your products app
            from tec.ecommerce.products.serializers import ProductSerializer 
            return ProductSerializer(instance.object, context=self.context).data
        
        # Add handlers for other models if indexed (e.g., 'category')
        
        return None
