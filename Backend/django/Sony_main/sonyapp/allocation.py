import json
from django.db import transaction, connection
from .models import RetailerOrder, Employee, Shipment

def reset_shipment_sequence():
    """
    Reset the shipment_id sequence so that the next shipment_id 
    is one greater than the current maximum in the sonyapp_shipment table.
    """
    with connection.cursor() as cursor:
        # Note: Adjust table and column names if necessary.
        cursor.execute(
            "SELECT setval(pg_get_serial_sequence('sonyapp_shipment', 'shipment_id'), "
            "COALESCE((SELECT MAX(shipment_id) FROM sonyapp_shipment), 0) + 1, false);"
        )

def allocate_shipments():
    try:
        # Reset shipment sequence to avoid duplicate primary key errors.
        reset_shipment_sequence()
        
        pending_orders = RetailerOrder.objects.filter(status='pending').select_related('retailer', 'order__product')
        employees = Employee.objects.select_related('truck').order_by('shipment_priority')

        # Map each valid truck's primary key (truck_id) to its capacity.
        truck_capacity = {e.truck.truck_id: e.truck.capacity for e in employees if e.truck}

        allocations = []

        for order in pending_orders:
            retailer = order.retailer
            order_details = order.order
            product = order_details.product

            # Check stock availability.
            if product.available_quantity < order_details.required_qty:
                allocations.append({
                    "order_id": order_details.order_id,
                    "status": "failed",
                    "reason": "Insufficient stock"
                })
                continue

            assigned_employee = None
            min_distance = float('inf')

            # Find the best employee with enough truck capacity.
            for employee in employees:
                if (employee.truck and 
                    truck_capacity.get(employee.truck.truck_id, 0) >= order_details.required_qty):
                    if retailer.distance_from_warehouse < min_distance:
                        assigned_employee = employee
                        min_distance = retailer.distance_from_warehouse

            if assigned_employee:
                with transaction.atomic():
                    # Update product stock.
                    product.available_quantity -= order_details.required_qty
                    product.total_shipped += order_details.required_qty
                    product.save(update_fields=['available_quantity', 'total_shipped'])

                    # Update order statuses.
                    order_details.status = 'allocated'
                    order_details.save(update_fields=['status'])
                    order.status = 'allocated'
                    order.save(update_fields=['status'])

                    # Reduce the truck's available capacity.
                    truck_capacity[assigned_employee.truck.truck_id] -= order_details.required_qty

                    # Create a Shipment record (Django auto-generates shipment_id).
                    shipment = Shipment.objects.create(
                        order=order_details,
                        truck=assigned_employee.truck,
                        employee=assigned_employee,
                        status='in_transit'
                    )

                    allocations.append({
                        "order_id": order_details.order_id,
                        "retailer": retailer.name,
                        "product": product.name,
                        "allocated_employee": assigned_employee.name,
                        "truck": assigned_employee.truck.license_plate,
                        "shipment_id": shipment.shipment_id,
                        "status": "allocated"
                    })

        return json.dumps({"allocations": allocations}, indent=4)

    except Exception as e:
        return json.dumps({"error": f"Unexpected Error: {str(e)}"}, indent=4)
