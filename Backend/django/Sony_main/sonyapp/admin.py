from django.contrib import admin
from .models import Category, Product, Retailer, Order, Employee, Truck, Shipment

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'available_quantity', 'total_required_quantity', 'status')
    search_fields = ('name',)
    list_filter = ('status',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'retailer', 'product', 'required_qty', 'status', 'order_date')
    search_fields = ('product__name', 'retailer__name')
    list_filter = ('status', 'order_date')

# Register other models
admin.site.register(Category)
admin.site.register(Retailer)
admin.site.register(Employee)
admin.site.register(Truck)
admin.site.register(Shipment)
