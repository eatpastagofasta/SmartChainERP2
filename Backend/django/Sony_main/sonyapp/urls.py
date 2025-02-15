from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomAuthToken, logout_view, get_employees, get_retailers,
    get_orders, allocate_orders, get_trucks, get_shipments
)

urlpatterns = [
    # ✅ Authentication Endpoints
    path('token/', CustomAuthToken.as_view(), name='api_token_auth'),  # Login (Returns JWT tokens)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh JWT token
    path('logout/', logout_view, name='api_logout'),  # Logout (Blacklist refresh token)

    # ✅ API Endpoints (Protected)
    path('employees/', get_employees, name='get_employees'),
    path('retailers/', get_retailers, name='get_retailers'),
    path('orders/', get_orders, name='get_orders'),
    path('allocate-orders/', allocate_orders, name='allocate_orders'),
    path('trucks/', get_trucks, name='get_trucks'),
    path('shipments/', get_shipments, name='get_shipments'),
]
