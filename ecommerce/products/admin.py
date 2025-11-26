from django.contrib import admin
from .models import Category, Product, ProductImage, Tag 
from django.utils.safestring import mark_safe # Used for displaying thumbnails

# ----------------------------------------------------
# 1. Product Image Inline (To manage images within the Product page)
# ----------------------------------------------------
class ProductImageInline(admin.TabularInline):
    """ Allows management of product images directly within the Product edit screen. """
    model = ProductImage
    extra = 1 # Number of empty forms to display by default
    fields = ('image', 'is_main')
    # You might add an image preview here using a method if needed

# ----------------------------------------------------
# 2. Product Admin (Configuration for the Product model)
# ----------------------------------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """ Configuration for displaying and editing the Product model in the Admin. """
    
    # Fields that appear in the list view
    list_display = (
        'name', 
        'category', 
        'seller', 
        'base_price_pi', 
        'inventory_stock', 
        'is_available',
        'is_featured', 
        'created_at'
    )
    
    # Fields that can be searched
    search_fields = ('name', 'description', 'seller__username')
    
    # Filters available on the right sidebar
    list_filter = ('is_available', 'is_featured', 'category', 'created_at')
    
    # Fields that are automatically populated (slug from name)
    prepopulated_fields = {'slug': ('name',)}
    
    # Grouping and ordering of fields in the detail view
    fieldsets = (
        ('Product Details', {
            'fields': ('name', 'slug', 'description', 'category', 'seller', 'tags')
        }),
        ('Pricing & Inventory', {
            'fields': ('base_price_pi', 'sale_price_pi', 'inventory_stock', 'rating_avg'),
            'description': "Pricing must be set in Pi currency."
        }),
        ('Status & Visibility', {
            'fields': ('is_available', 'is_featured'),
            'classes': ('collapse',), # Collapsed by default
        }),
    )
    
    # Embed the image inline class into the product screen
    inlines = [ProductImageInline]

# ----------------------------------------------------
# 3. Category Admin (Configuration for the Category model)
# ----------------------------------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """ Configuration for displaying and editing the Category model. """
    
    list_display = ('name', 'parent', 'slug')
    search_fields = ('name',)
    list_filter = ('parent',)
    prepopulated_fields = {'slug': ('name',)}
    
    # Number of items per page
    list_per_page = 20

# ----------------------------------------------------
# 4. Tag Admin (Configuration for the Tag model - if used)
# ----------------------------------------------------
if 'Tag' in locals():
    @admin.register(Tag)
    class TagAdmin(admin.ModelAdmin):
        list_display = ('name', 'slug')
        search_fields = ('name',)
        prepopulated_fields = {'slug': ('name',)}
