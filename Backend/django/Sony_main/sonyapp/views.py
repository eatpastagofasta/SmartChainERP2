import json
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import Employee, Retailer, Order, Truck, Shipment
from .serializers import EmployeeSerializer, RetailerSerializer, OrderSerializer, TruckSerializer, ShipmentSerializer
from .allocation import allocate_shipments

# ✅ Custom Pagination Class
class StandardPagination(PageNumberPagination):
    page_size = 10  # Customize per need
    page_size_query_param = 'page_size'
    max_page_size = 100

# ✅ Custom JWT Login View
class CustomAuthToken(TokenObtainPairView):
    """
    Custom authentication to generate access and refresh tokens.
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = request.user
        return Response({
            'access': response.data['access'],
            'refresh': response.data['refresh'],
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_200_OK)

# ✅ Logout View (Blacklist Refresh Token)
@api_view(['POST'])
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

# ✅ Get Employees (Protected, Paginated)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_employees(request):
    try:
        employees = Employee.objects.all()
        paginator = StandardPagination()
        paginated_employees = paginator.paginate_queryset(employees, request)
        serializer = EmployeeSerializer(paginated_employees, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ✅ Get Retailers (Protected, Paginated)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_retailers(request):
    try:
        retailers = Retailer.objects.all()
        paginator = StandardPagination()
        paginated_retailers = paginator.paginate_queryset(retailers, request)
        serializer = RetailerSerializer(paginated_retailers, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ✅ Get Orders (Protected, Paginated, Filterable)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):
    try:
        status_filter = request.GET.get('status')  # Optional filter
        orders = Order.objects.all().order_by('-created_at')

        if status_filter:
            orders = orders.filter(status=status_filter)

        paginator = StandardPagination()
        paginated_orders = paginator.paginate_queryset(orders, request)
        serializer = OrderSerializer(paginated_orders, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ✅ Allocate Orders (Protected)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def allocate_orders(request):
    try:
        allocation_result = json.loads(allocate_shipments())  # Convert JSON string to dict
        return Response(allocation_result, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ✅ Get Trucks (Protected, Paginated)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trucks(request):
    try:
        trucks = Truck.objects.all()
        paginator = StandardPagination()
        paginated_trucks = paginator.paginate_queryset(trucks, request)
        serializer = TruckSerializer(paginated_trucks, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ✅ Get Shipments (Protected, Paginated)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_shipments(request):
    try:
        shipments = Shipment.objects.all().order_by('-created_at')
        paginator = StandardPagination()
        paginated_shipments = paginator.paginate_queryset(shipments, request)
        serializer = ShipmentSerializer(paginated_shipments, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
