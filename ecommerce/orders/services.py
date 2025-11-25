from django.db import transaction, DatabaseError
from products.models import Product  # Import the Product model
from .models import Order, OrderDetail # Import Order models

# Define a custom error for inventory issues
class InsufficientStockError(Exception):
    pass

def process_order_and_deduct_inventory(customer_id: int, cart_data: list, shipping_address: str):
    """
    Processes the entire order within a single, secure database transaction.
    Uses select_for_update to handle concurrency and prevent overselling.
    """
    try:
        # Start the atomic block (all or nothing)
        with transaction.atomic():
            
            total_order_amount = 0
            
            # 1. Create the base Order record
            order = Order.objects.create(
                customer_id=customer_id,
                status='PENDING',
                shipping_address=shipping_address,
                # total_amount will be updated at the end
            )

            # 2. Iterate through items, validate stock, and deduct inventory
            for item in cart_data:
                product_id = item.get('product_id')
                quantity = item.get('quantity')
                
                # Lock the product row to prevent simultaneous purchase (Concurrency Control)
                product = Product.objects.select_for_update().get(id=product_id)

                if product.inventory_stock < quantity:
                    # If stock is insufficient, raise a custom error to trigger ROLLBACK
                    raise InsufficientStockError(f"Stock not available for Product ID: {product_id}")

                # Deduct inventory
                product.inventory_stock -= quantity
                product.save()

                # Add Order Detail record
                OrderDetail.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.base_price 
                )
                
                total_order_amount += product.base_price * quantity
            
            # 3. Final updates and status change
            order.total_amount = total_order_amount
            # Assume successful payment (Payment logic goes here)
            order.status = 'PROCESSING' 
            order.save()
            
            # 4. (Next Step) Trigger notification service call here
            # notification_service.send_order_confirmation(customer_id, order.id)
            
            return {"success": True, "order_id": order.id}

    except InsufficientStockError as e:
        return {"success": False, "error": str(e)}
        
    except DatabaseError:
        # Generic database failure (e.g., connection issue)
        return {"success": False, "error": "Database error occurred. Please try again."}
    
    except Exception as e:
        return {"success": False, "error": f"An unexpected error occurred: {str(e)}"}
