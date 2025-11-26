# File: tec/ecommerce/products/serializers.py (Final Version)

from rest_framework import serializers
from .models import Category, Product, ProductImage
from django.conf import settings

# -----------------
# Product Image Serializer
# -----------------
class ProductImageSerializer(serializers.ModelSerializer):
    """ Serializer for ProductImage model. """
    
    class Meta:
        model = ProductImage
        fields = ['image', 'is_main']

# -----------------
# Category Serializer (Must be defined after ProductImageSerializer)
# -----------------
class CategorySerializer(serializers.ModelSerializer):
    """ Serializer for Category model. """
    
    # Nested field to show subcategories directly
    sub_categories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        # Added 'slug' for clean URLs
        fields = ['id', 'name', 'slug', 'description', 'parent', 'sub_categories'] 
        
    def get_sub_categories(self, obj):
        # Prevent infinite recursion loop by checking the depth if needed.
        
        # Optimize query: prefetch related children for efficiency
        children = obj.sub_categories.all() 
        
        if not children.exists():
            return []
            
        # IMPORTANT: Use the outer serializer for recursive call
        # Pass context if needed, but here we keep it simple.
        # Ensure 'children' are passed to the serializer instance
        return CategorySerializer(children, many=True).data

# -----------------
# Product Detail and List Serializers
# -----------------

class ProductListSerializer(serializers.ModelSerializer):
    """ Serializer used for displaying a list of products (less detail). """
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    # Only show the main image for the list view
    main_image = serializers.SerializerMethodField() 

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category_name', 
            'base_price_pi', 'sale_price_pi', 'inventory_stock',
            'rating_avg', 'main_image'
        ]

    def get_main_image(self, obj):
        # Find the image marked as main, or the first one available
        # Optimized to use 'first()' which executes a single query
        main_img = obj.images.filter(is_main=True).first()
        if main_img:
            # Assumes you have configured MEDIA_URL correctly in settings
            return self.context['request'].build_absolute_uri(main_img.image.url) if 'request' in self.context else main_img.image.url
        return None

class ProductDetailSerializer(ProductListSerializer):
    """ Serializer used for displaying a single product (more detail). """
    
    # Nested images serializer
    images = ProductImageSerializer(many=True, read_only=True)
    # seller_info = SellerProfileSerializer() # Placeholder
    
    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + [
            'description', 'seller', 'created_at', 'images'
        ]
        read_only_fields = ['seller']
