from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Order, Product

@receiver(pre_save, sender=Order)
def store_old_order_status(sender, instance, **kwargs):
    """Stores the old order status and quantity before saving"""
    try:
        old_order = Order.objects.get(pk=instance.pk)
        instance._old_status = old_order.status
        instance._old_required_qty = old_order.required_qty
    except Order.DoesNotExist:
        instance._old_status = None
        instance._old_required_qty = None

@receiver(post_save, sender=Order)
def update_product_required_quantity_on_save(sender, instance, created, **kwargs):
    """
    Updates total_required_quantity in Product when an Order is created or updated.
    Ensures total_required_quantity never becomes negative.
    """
    product = instance.product

    if created:
        # If order is newly created with 'pending' or 'allocated' status, add required_qty
        if instance.status in ['pending', 'allocated']:
            product.total_required_quantity += instance.required_qty
    else:
        old_status = instance._old_status
        old_required_qty = instance._old_required_qty

        # Case 1: Order status changes from 'pending/allocated' → 'delivered' or 'canceled'
        if old_status in ['pending', 'allocated'] and instance.status in ['delivered', 'canceled']:
            product.total_required_quantity = max(0, product.total_required_quantity - old_required_qty)

        # Case 2: Order status changes from 'delivered/canceled' → 'pending' or 'allocated'
        elif old_status in ['delivered', 'canceled'] and instance.status in ['pending', 'allocated']:
            product.total_required_quantity += instance.required_qty

        # Case 3: Order quantity changes while keeping the status in 'pending' or 'allocated'
        elif old_status in ['pending', 'allocated'] and instance.status in ['pending', 'allocated']:
            quantity_difference = instance.required_qty - old_required_qty
            product.total_required_quantity = max(0, product.total_required_quantity + quantity_difference)

    product.save()

@receiver(post_delete, sender=Order)
def update_product_required_quantity_on_delete(sender, instance, **kwargs):
    """
    Subtract required_qty from total_required_quantity when an order is deleted.
    Ensures total_required_quantity never becomes negative.
    """
    if instance.status in ['pending', 'allocated']:
        product = instance.product
        product.total_required_quantity = max(0, product.total_required_quantity - instance.required_qty)
        product.save()
