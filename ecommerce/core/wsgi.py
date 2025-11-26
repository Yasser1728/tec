# File: tec/ecommerce/core/wsgi.py

import os

from django.core.wsgi import get_wsgi_application

# Ensure the environment variable points to the correct settings file
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tec.ecommerce.core.settings')

application = get_wsgi_application()
