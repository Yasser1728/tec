# File: tec/ecommerce/core/settings.py

import os
from pathlib import Path
import dj_database_url

# -----------------------------------------------------------------
# 1. BASE CONFIGURATION
# -----------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------
# 2. SECURITY SETTINGS (Crucial for Production)
# -----------------------------------------------------------------
# SECRET_KEY and DEBUG must be pulled from environment variables
SECRET_KEY = os.environ.get('SECRET_KEY', 'default-insecure-key-for-dev-only')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

# -----------------------------------------------------------------
# 3. APPLICATION DEFINITION (Installed Apps)
# -----------------------------------------------------------------
INSTALLED_APPS = [
    # Django Built-in Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party Apps
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters', 
    
    # 🌟 Your Project Apps (Commerce.PI Modules)
    'accounts.apps.AccountsConfig',
    'products.apps.ProductsConfig',
    'orders.apps.OrdersConfig',
    'growth.apps.GrowthConfig',
    'notifications.apps.NotificationsConfig',
    # Include 'search' if you have an app for it:
    # 'search.apps.SearchConfig', 
]

# -----------------------------------------------------------------
# 4. MIDDLEWARE & URLS
# -----------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# -----------------------------------------------------------------
# 5. DATABASE CONFIGURATION
# -----------------------------------------------------------------
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600 
    )
}

# -----------------------------------------------------------------
# 6. AUTHENTICATION & USER MODEL (CRITICAL FOR ACCOUNTS)
# -----------------------------------------------------------------
# 🌟 MUST BE SET TO USE CustomUser model
AUTH_USER_MODEL = 'accounts.CustomUser' 

# Django Password Validation (Adjust MinimumLength as needed)
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# -----------------------------------------------------------------
# 7. DRF & JWT CONFIGURATION
# -----------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# -----------------------------------------------------------------
# 8. PI NETWORK & CUSTOM ECOMMERCE SETTINGS
# -----------------------------------------------------------------
# Pi Network API Keys and Configuration
PI_NETWORK_API_KEY = os.environ.get('PI_NETWORK_API_KEY', 'default_pi_key')
PI_APP_CLIENT_ID = os.environ.get('PI_APP_CLIENT_ID', 'pi_app_id')
# Default time for escrow release (e.g., 14 days after shipment)
PI_ESCROW_RELEASE_DAYS = int(os.environ.get('PI_ESCROW_RELEASE_DAYS', 14)) 

# -----------------------------------------------------------------
# 9. INTERNATIONALIZATION
# -----------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------
# 10. STATIC & MEDIA FILES
# -----------------------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# -----------------------------------------------------------------
# 11. EMAIL/NOTIFICATION CONFIGURATION
# -----------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@commercepi.com')

# -----------------------------------------------------------------
# 12. ELASTICSEARCH CONFIGURATION (For Search)
# -----------------------------------------------------------------
ELASTIC_HOST = os.environ.get('ELASTIC_HOST', 'http://localhost:9200')
ELASTIC_USER = os.environ.get('ELASTIC_USER', '')
ELASTIC_PASSWORD = os.environ.get('ELASTIC_PASSWORD', '')
