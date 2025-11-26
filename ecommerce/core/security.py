# File: tec/ecommerce/core/security.py

import os
from datetime import timedelta

# 1. Security Core Settings
# ملاحظة هامة: يجب تحميل مفتاح السرية من متغيرات البيئة في بيئة الإنتاج
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'default-insecure-key-for-development')

# هذا يجب أن يتم تجاوزه (Overridden) في settings_prod.py
DEBUG = True 

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
# يجب إضافة أسماء النطاقات (Domain names) الخاصة بك هنا في الإنتاج

# 2. CORS (Cross-Origin Resource Sharing) Settings
CORS_ALLOW_ALL_ORIGINS = True # تغيير هذا إلى False في الإنتاج
CORS_ALLOW_CREDENTIALS = True 

# 3. Custom User Model
AUTH_USER_MODEL = 'accounts.User' 

# 4. Django REST Framework Settings
REST_FRAMEWORK = {
    # استخدام JWT كطريقة مصادقة افتراضية
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # إعدادات الصلاحيات الافتراضية: يجب أن يكون المستخدم مصادقاً (مسجل دخول)
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    # إعدادات ترقيم الصفحات (Pagination)
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
