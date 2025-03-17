import json
from django.db import transaction
from django.shortcuts import render
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
from django.db.models import F

from django.shortcuts import redirect

def redirect_view(request):
    return redirect('/admin/')

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

# ✅ MQTT Client View
def mqtt_client_view(request):
    return render(request, 'mqtt_client.html')

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

import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Category, Product

logger = logging.getLogger(_name_)

@api_view(['POST'])
@permission_classes([AllowAny])
def store_qr_code(request):
    """API to process and store QR code data into the Product model"""
    try:
        qr_data = request.data.get("qr_text", "").strip()  # Get and clean QR text
        logger.info(f"Received QR data: {qr_data}")

        if not qr_data:
            return Response({"error": "QR Code data is empty"}, status=400)

        # Safe parsing
        try:
            data_dict = {}
            for item in qr_data.split("|"):
                if "=" in item:
                    key, value = item.split("=", 1)  # Ensure only one split
                    data_dict[key] = value
        except ValueError as e:
            logger.error(f"Error parsing QR code data: {e}")
            return Response({"error": "Invalid QR Code data format"}, status=400)

        logger.info(f"Parsed QR data: {data_dict}")

        product_name = data_dict.get("name", "").strip()
        category_name = data_dict.get("category", "").strip()
        quantity_str = data_dict.get("quantity", "0").strip()

        # Validate quantity
        if not quantity_str.isdigit():
            logger.error("Quantity must be a positive integer.")
            return Response({"error": "Quantity must be a positive integer"}, status=400)

        quantity = int(quantity_str)

        # Validate data
        if not product_name or not category_name or quantity <= 0:
            logger.error(f"Invalid QR Code data: product_name={product_name}, category_name={category_name}, quantity={quantity}")
            return Response({"error": "Invalid QR Code data"}, status=400)

        # Fetch or create the category
        category, _ = Category.objects.get_or_create(name=category_name)
        logger.info(f"Category: {category.name}")

        # Fetch or create the product
        product, created = Product.objects.get_or_create(
            name=product_name,
            category=category,
            defaults={'available_quantity': 0}  # Ensure available_quantity is initialized
        )

        logger.info(f"Product: {product.name}, Created: {created}")

        # Update available quantity
        product.available_quantity += quantity
        product.save()
        logger.info(f"Updated product {product_name} with quantity {quantity}. New available quantity: {product.available_quantity}")

        return Response({"success": "QR Code data stored successfully"}, status=200)

    except Exception as e:
        logger.error(f"Error processing QR code data: {str(e)}")
        return Response({"error": str(e)}, status=500)