# File: tec/ecommerce/core/database.py

from pathlib import Path

# Define the project's base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Database configuration (SQLite default)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Add support for production databases (e.g., PostgreSQL using dj_database_url) here if needed
# import dj_database_url
# DATABASES['default'] = dj_database_url.config(conn_max_age=600)
