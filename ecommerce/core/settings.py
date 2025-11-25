# --- 1. SECURITY SETTINGS ---
# Pull the Secret Key from environment variables (crucial for security)
SECRET_KEY = os.environ.get('SECRET_KEY', 'default-insecure-key-for-dev-only')

# Set Debug Mode (False in production)
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Define allowed hosts (your domain names)
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# --- 2. INSTALLED APPS ---
# Ensure all new modules are registered here
INSTALLED_APPS = [
    # ... (Django and third-party apps usually go first)
    'ecommerce.accounts',
    'ecommerce.products',
    'ecommerce.orders',
    'ecommerce.growth',
    'ecommerce.notifications',
    'rest_framework',
    # ...
]

# --- 3. DATABASE CONFIGURATION ---
# Uses dj_database_url to parse the database URL from an environment variable (PostgreSQL recommended)
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'), # Should point to your PostgreSQL DB
        conn_max_age=600 # Recommended for persistent PostgreSQL connections
    )
}

# --- 4. ELASTICSEARCH CONFIGURATION ---
# Settings for the Search Service
ELASTIC_HOST = os.environ.get('ELASTIC_HOST', 'http://localhost:9200')
ELASTIC_USER = os.environ.get('ELASTIC_USER', '')
ELASTIC_PASSWORD = os.environ.get('ELASTIC_PASSWORD', '')

# --- 5. EMAIL/NOTIFICATION CONFIGURATION ---
# Settings for the Notification Service (SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True 
