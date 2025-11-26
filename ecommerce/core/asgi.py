# File: tec/ecommerce/core/asgi.py

import os

from django.core.asgi import get_asgi_application

# Ensure the environment variable points to the correct settings file
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tec.ecommerce.core.settings')

application = get_asgi_application()
