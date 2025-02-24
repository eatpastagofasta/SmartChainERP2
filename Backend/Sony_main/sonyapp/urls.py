from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.urlpatterns import format_suffix_patterns  # ✅ For better API format handling
from .views import (
    CustomAuthToken, logout_view, get_employees, get_retailers,
    get_orders, allocate_orders, get_trucks, get_shipments,get_stock_data,category_stock_data
)

urlpatterns = [
    # ✅ Authentication Endpoints
    path("token/", CustomAuthToken.as_view(), name="api_token_auth"),  # Login (Returns JWT tokens)
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),  # Refresh JWT token
    path("logout/", logout_view, name="api_logout"),  # Logout (Blacklist refresh token)

    # ✅ API Endpoints (Protected)
    path("employees/", get_employees, name="get_employees"),  # Admin Only
    path("retailers/", get_retailers, name="get_retailers"),  # Admin Only
    path("orders/", get_orders, name="get_orders"),  # Admin & Employees
    path("allocate-orders/", allocate_orders, name="allocate_orders"),  # Employees Only
    path("trucks/", get_trucks, name="get_trucks"),  # Admin Only
    path("shipments/", get_shipments, name="get_shipments"),  # Admin & Employees.
    path('stock/', get_stock_data, name='stock-data'),
    path('category-stock/', category_stock_data, name='category-stock-data'),
]

# ✅ Support API requests with format suffixes (e.g., `/orders.json`, `/orders.xml`)
urlpatterns = format_suffix_patterns(urlpatterns, allowed=["json", "html"])
