from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.conf import settings
from .models import CustomUser, UserProfile # Assuming CustomUser and UserProfile exist

# Use the AUTH_USER_MODEL from settings
User = settings.AUTH_USER_MODEL

# ----------------------------------------------------
# User Profile Inline
# ----------------------------------------------------
class UserProfileInline(admin.StackedInline):
    """ Displays the related UserProfile fields within the CustomUser edit screen. """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

# ----------------------------------------------------
# Custom User Admin Configuration
# ----------------------------------------------------
@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """
    Custom administration panel for the CustomUser model.
    It extends the default Django UserAdmin.
    """
    # Fields that appear in the list view
    list_display = (
        'username', 
        'email', 
        'is_active', 
        'is_staff', 
        'is_seller', # Assuming this field exists for seller role
        'date_joined'
    )
    
    # Filters available on the right sidebar
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'is_seller')
    
    # Fields to search by
    search_fields = ('username', 'email')

    # Customize the fieldsets for the detail view
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email',)}), # Add other custom fields here
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_seller', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Add the profile inline to the user admin screen
    inlines = (UserProfileInline,)

# NOTE: If you have an address model, you should also register it here.
