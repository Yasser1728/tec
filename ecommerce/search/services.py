import elasticsearch
from elasticsearch import Elasticsearch
from products.models import Product
from django.conf import settings
from typing import List, Dict

# Assuming Elasticsearch connection details are in Django settings
ES_CLIENT = Elasticsearch(
    [settings.ELASTIC_HOST],
    http_auth=(settings.ELASTIC_USER, settings.ELASTIC_PASSWORD)
)
INDEX_NAME = 'product_index'

def index_product(product: Product):
    """
    Indexes or updates a single product document in Elasticsearch.
    """
    try:
        # 1. Prepare the document data
        product_doc = {
            'product_id': product.id,
            'name': product.name_en,
            'description': product.description_en,
            'price': float(product.sale_price if product.sale_price else product.base_price),
            'category_id': product.category_id,
            'rating_avg': float(product.rating_avg),
            'inventory': product.inventory_stock,
            'is_available': product.inventory_stock > 0,
            # Add attributes like color, size, brand here if they exist in the model
        }

        # 2. Index the document
        ES_CLIENT.index(
            index=INDEX_NAME,
            id=product.id,
            document=product_doc
        )
        return {"success": True}

    except Exception as e:
        print(f"Error indexing product {product.id}: {e}")
        return {"success": False, "error": str(e)}


def search_products(query: str, filters: Dict = None, sort_by: str = '-rating_avg') -> List[Dict]:
    """
    Executes a complex search and filter query against Elasticsearch.
    """
    try:
        # Define the basic search query (matching product name or description)
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {"multi_match": {"query": query, "fields": ["name^3", "description"]}}
                    ]
                }
            },
            "sort": [
                {sort_by.lstrip('-'): {"order": "desc" if sort_by.startswith('-') else "asc"}}
            ]
        }
        
        # Add filtering logic (e.g., category, price range)
        if filters:
            if 'category_id' in filters:
                search_body['query']['bool']['filter'] = [
                    {"term": {"category_id": filters['category_id']}}
                ]
            # Add more filters (price range, brand, etc.) here...

        res = ES_CLIENT.search(index=INDEX_NAME, body=search_body)
        
        # Return only the relevant product IDs and scores
        results = [hit['_source'] for hit in res['hits']['hits']]
        return results

    except Exception as e:
        print(f"Error executing search: {e}")
        return []
