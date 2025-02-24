import json
from django.db import transaction
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count
from .models import Employee, Retailer, Order, Truck, Shipment, Product, Category
from .serializers import (
    EmployeeSerializer, RetailerSerializer, 
    OrderSerializer, ProductSerializer, TruckSerializer, ShipmentSerializer, CategorySerializer
)
from .allocation import allocate_shipments
from .permissions import IsAdminUser

# ✅ Custom Pagination Class
class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

# ✅ Custom JWT Login View
class CustomAuthToken(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = request.user
        return Response(
            {
                "access": response.data["access"],
                "refresh": response.data["refresh"],
                "user_id": user.id,
                "username": user.username,
            },
            status=status.HTTP_200_OK,
        )

# ✅ Logout View (Blacklist Refresh Token)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ✅ Get Employees (Admin Only)
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_employees(request):
    try:
        employees = Employee.objects.all()
        paginator = StandardPagination()
        paginated_employees = paginator.paginate_queryset(employees, request)
        serializer = EmployeeSerializer(paginated_employees, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ✅ Get Retailers (Admin Only)
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_retailers(request):
    try:
        retailers = Retailer.objects.all()
        paginator = StandardPagination()
        paginated_retailers = paginator.paginate_queryset(retailers, request)
        serializer = RetailerSerializer(paginated_retailers, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ✅ Get Orders (Anyone Logged In)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_orders(request):
    try:
        status_filter = request.GET.get("status")
        orders = Order.objects.all().order_by("-order_date")

        if status_filter:
            orders = orders.filter(status=status_filter)

        paginator = StandardPagination()
        paginated_orders = paginator.paginate_queryset(orders, request)
        serializer = OrderSerializer(paginated_orders, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ✅ Get Trucks (Admin Only)
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_trucks(request):
    try:
        trucks = Truck.objects.all()
        paginator = StandardPagination()
        paginated_trucks = paginator.paginate_queryset(trucks, request)
        serializer = TruckSerializer(paginated_trucks, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ✅ Get Shipments (Anyone Logged In)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_shipments(request):
    try:
        shipments = Shipment.objects.all().order_by("-created_at")
        paginator = StandardPagination()
        paginated_shipments = paginator.paginate_queryset(shipments, request)
        serializer = ShipmentSerializer(paginated_shipments, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@permission_classes([IsAuthenticated])  
def allocate_orders(request):
    try:
        with transaction.atomic():
            allocation_result = allocate_shipments(request)

            if isinstance(allocation_result, Response):
                return allocation_result

            # ✅ Ensure all product statuses are updated
            products = Product.objects.all()
            for product in products:
                product.save()  # This will call update_status() before saving

        return Response(
            {"message": "Orders allocated and stock status updated successfully"},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ✅ Get Stock Data (Admin Only)
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_stock_data(request):
    if not request.user.is_staff:
        return Response({"detail": "Access denied. Admins only."}, status=status.HTTP_403_FORBIDDEN)

    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

# ✅ Get Category Stock Data (Accessible by Anyone)
@api_view(["GET"])
def category_stock_data(request):
    """
    Returns category names and product count for visualization.
    """
    try:
        categories = Category.objects.annotate(product_count=Count('products'))  # ✅ Count products per category

        # Serialize the data
        serialized_data = CategorySerializer(categories, many=True).data

        # Attach product_count to each category in serialized data
        for category in serialized_data:
            category["value"] = next(
                (cat["product_count"] for cat in categories.values("name", "product_count") if cat["name"] == category["name"]),
                0
            )

        return Response({"success": True, "data": serialized_data})
    except Exception as e:
        return Response({"error": str(e)}, status=500)
