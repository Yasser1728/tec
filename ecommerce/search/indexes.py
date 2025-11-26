# File: tec/ecommerce/search/indexes.py

from haystack import indexes
# Import your product models
from tec.ecommerce.products.models import Product, Category 

# ----------------------------------------------------
# 1. Product Index
# ----------------------------------------------------
class ProductIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Defines how the Product model should be indexed by Elasticsearch.
    """
    # The main field used for searching. 'document=True' marks it as the primary 
    # search field, and 'use_template=True' means its content is defined in a separate template.
    text = indexes.CharField(document=True, use_template=True)
    
    # Fields for filtering, sorting, and display
    name = indexes.CharField(model_attr='name', faceted=True)
    description = indexes.CharField(model_attr='description')
    price = indexes.DecimalField(model_attr='base_price_pi')
    category_name = indexes.CharField(model_attr='category__name', faceted=True)
    seller_name = indexes.CharField(model_attr='seller__username', faceted=True)
    is_available = indexes.BooleanField(model_attr='is_available')

    def get_model(self):
        """ Returns the model that this index is for. """
        return Product

    def index_queryset(self, using=None):
        """ Used when the entire index for the model is updated (e.g., 'rebuild_index'). """
        # Only index products that are marked as available
        return self.get_model().objects.filter(is_available=True)

# ----------------------------------------------------
# 2. Category Index (Optional)
# ----------------------------------------------------
class CategoryIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Defines how the Category model should be indexed for category-specific search.
    """
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')

    def get_model(self):
        return Category

# NOTE: To use 'use_template=True' correctly, you must create a file 
# like: tec/ecommerce/search/templates/search/indexes/products/product_text.txt
# which defines what fields should be combined into the 'text' field (e.g., {{ object.name }} {{ object.description }})
