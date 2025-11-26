# File: tec/ecommerce/core/security.py

import os
from datetime import timedelta

# 1. Security Core Settings
# IMPORTANT: Load SECRET_KEY from environment variables in production
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'default-insecure-key-for-development')

# This should be overridden in settings_prod.py for production
DEBUG = True 

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
# Add your production domain names here when DEBUG is False

# 2. CORS (Cross-Origin Resource Sharing) Settings
CORS_ALLOW_ALL_ORIGINS = True # Change this to False in production
CORS_ALLOW_CREDENTIALS = True 

# 3. Custom User Model
AUTH_USER_MODEL = 'accounts.User' 

# 4. Django REST Framework Settings
REST_FRAMEWORK = {
    # Default authentication: JWT (JSON Web Tokens)
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # Default permission: User must be authenticated
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    # Pagination setup
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# 5. Simple JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
