from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Employee, Retailer, Order, RetailerOrder, Truck, Shipment
from .serializers import EmployeeSerializer, RetailerSerializer, OrderSerializer, RetailerOrderSerializer, TruckSerializer, ShipmentSerializer
from .allocation import allocate_shipments
from rest_framework import status

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

# ✅ Get Employees (Protected)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_employees(request):
    employees = Employee.objects.all()
    serializer = EmployeeSerializer(employees, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# ✅ Get Retailers (Protected)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_retailers(request):
    retailers = Retailer.objects.all()
    serializer = RetailerSerializer(retailers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# ✅ Get Orders (Protected)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# ✅ Allocate Orders (Protected)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def allocate_orders(request):
    allocation_result = allocate_shipments()
    return Response(allocation_result, content_type="application/json", status=status.HTTP_200_OK)

# ✅ Get Trucks (Protected)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trucks(request):
    trucks = Truck.objects.all()
    serializer = TruckSerializer(trucks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# ✅ Get Shipments (Protected)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_shipments(request):
    shipments = Shipment.objects.all()
    serializer = ShipmentSerializer(shipments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
