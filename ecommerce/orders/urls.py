# File: Ecom-backend-django/orders/urls.py

from django.urls import path
from . import views
from .views import CheckoutPiAPIView, CompleteOrderAPIView # استيراد الدالات الصحيحة

urlpatterns = [
    # 1. API Endpoint لإنشاء الطلب وبدء الضمان (Escrow Lock)
    # /api/orders/checkout/
    path('checkout/', CheckoutPiAPIView.as_view(), name='pi-checkout'),

    # 2. API Endpoint لإنهاء الطلب وتحرير أموال Pi (يتم استدعاؤها من قبل المشتري)
    # /api/orders/123/complete/
    path('<int:order_id>/complete/', CompleteOrderAPIView.as_view(), name='complete-order'),
    
    # يمكنك إضافة مسارات أخرى هنا لعرض قائمة وتفاصيل الطلبات:
    # path('', views.OrderListAPIView.as_view(), name='order-list'),
    # path('<int:order_id>/', views.OrderDetailAPIView.as_view(), name='order-detail'),
]
