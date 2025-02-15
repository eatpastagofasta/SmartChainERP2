from django.db import models

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    available_quantity = models.PositiveIntegerField()
    total_shipped = models.PositiveIntegerField(default=0)
    total_required_quantity = models.PositiveIntegerField(default=0)

    STATUS_CHOICES = [
        ('on_demand', 'On Demand'),
        ('sufficient', 'Sufficient')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sufficient')

    def __str__(self):
        return self.name

class Retailer(models.Model):
    retailer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact = models.CharField(max_length=20)
    distance_from_warehouse = models.FloatField()

    def __str__(self):
        return self.name

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    required_qty = models.PositiveIntegerField()
    order_date = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('allocated', 'Allocated'),
        ('cancelled', 'Cancelled')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order {self.order_id} - {self.product.name}"

class RetailerOrder(models.Model):
    retailer = models.ForeignKey(Retailer, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('allocated', 'Allocated'),
        ('cancelled', 'Cancelled')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        unique_together = ('retailer', 'order')

    def __str__(self):
        return f"Retailer {self.retailer.name} - Order {self.order.order_id}"

class Truck(models.Model):
    truck_id = models.AutoField(primary_key=True)
    license_plate = models.CharField(max_length=20, unique=True)
    capacity = models.PositiveIntegerField(help_text="Maximum shipment capacity")

    def __str__(self):
        return self.license_plate

class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=20)
    truck = models.OneToOneField(Truck, on_delete=models.CASCADE)
    shipment_priority = models.IntegerField(help_text="Lower value indicates higher priority")

    def __str__(self):
        return f"{self.name} (Truck: {self.truck.license_plate})"

class Shipment(models.Model):
    shipment_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    shipment_date = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_transit')

    def __str__(self):
        return f"Shipment {self.shipment_id} - {self.truck.license_plate}"
    



