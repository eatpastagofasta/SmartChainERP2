from django.contrib import admin
from django.contrib.auth.models import User
from .models import Category, Product, Retailer, Order, Employee, Truck, Shipment

# ✅ Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'name')  # Changed 'id' to 'category_id'
    search_fields = ('name',)


# ✅ Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'name', 'category', 'available_quantity', 'total_required_quantity', 'status')  # Changed 'id' to 'product_id'
    search_fields = ('name',)
    list_filter = ('status',)


# ✅ Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'retailer', 'product', 'required_qty', 'status', 'order_date')  # Changed 'id' to 'order_id'
    search_fields = ('product__name', 'retailer__name')
    list_filter = ('status', 'order_date')


# ✅ Employee Admin (Filtered Dropdown to Show Only "Employee" Users)
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact', 'truck')  # Removed 'employee_id' (assuming 'user' is the main identifier)
    search_fields = ('user__username', 'contact')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(is_superuser=False, groups__name="employee")  # Exclude superusers, show only "Employee" users
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# ✅ Retailer Admin
@admin.register(Retailer)
class RetailerAdmin(admin.ModelAdmin):
    list_display = ('retailer_id', 'name', 'address', 'contact', 'distance_from_warehouse')  # Changed 'id' to 'retailer_id'
    search_fields = ('name', 'address')


# ✅ Truck Admin
@admin.register(Truck)
class TruckAdmin(admin.ModelAdmin):
    list_display = ('truck_id', 'license_plate', 'capacity', 'is_available')  # Changed 'id' to 'truck_id'
    search_fields = ('license_plate',)


# ✅ Shipment Admin
@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('shipment_id', 'order', 'employee', 'status', 'shipment_date')  # Changed 'id' to 'shipment_id'
    search_fields = ('order__order_id', 'employee__user__username')  # Fetch employee name properly
    list_filter = ('status', 'shipment_date')
