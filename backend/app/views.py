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
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Employee, Retailer, Order, Truck, Shipment, Product, Category, QRScan
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

# ✅ MQTT Client View
def mqtt_client_view(request):
    return render(request, 'mqtt_client.html')

# ✅ Save QR Data
@csrf_exempt
def store_qr_code(request):
    if request.method == 'POST':
        try:
            # ✅ Debugging: Print the exact raw request body
            raw_body = request.body.decode('utf-8')
            print(f"[🧐] Raw Request Body: {raw_body}")

            # ✅ Parse JSON
            data = json.loads(raw_body)
            qr_text = data.get("qr_text", "").strip()  # Get the value of qr_text
            
            # ✅ Debugging: Ensure extracted text is correct
            print(f"[✅] Extracted QR Text: {qr_text}")

            if not qr_text:
                return JsonResponse({'success': False, 'error': 'QR text is empty'}, status=400)

            # ✅ Store raw QR text in QRScan model
            scan = QRScan.objects.create(data=qr_text, processed=False)

            # ✅ Extract product details from QR text
            product_data = {}
            for pair in qr_text.split('|'):
                key_value = pair.split('=', 1)
                if len(key_value) == 2:
                    product_data[key_value[0].strip()] = key_value[1].strip()

            # ✅ Extract values
            name = product_data.get("name")
            category_name = product_data.get("category")
            quantity_str = product_data.get("quantity")

            if not name or not category_name or not quantity_str:
                return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)

            # ✅ Convert quantity to integer
            try:
                quantity = int(quantity_str)
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid quantity format'}, status=400)

            # ✅ Update Product and Category tables
            category, _ = Category.objects.get_or_create(name=category_name)
            product, _ = Product.objects.get_or_create(
                name=name, category=category, defaults={'available_quantity': 0}
            )

            product.available_quantity += quantity
            product.save()

            scan.processed = True
            scan.save()

            return JsonResponse({
                'success': True,
                'message': 'QR data processed successfully',
                'product_id': product.product_id,
                'available_quantity': product.available_quantity
            })

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON format'}, status=400)

        except Exception as e:
            print(f"[❌] Error processing QR code: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)