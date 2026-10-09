"""
Order Management Service handling checkout, stock reservation, status transitions, and tracking.
"""
from typing import List, Optional, Dict, Any
import uuid
import random
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.order_repository import OrderRepository, AddressRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.cart_repository import CartRepository
from app.models.sql_models import Order, OrderItem, Inventory
from app.schemas.all_schemas import OrderCreate
from app.exceptions import NotFoundError, BadRequestError, InsufficientStockError

class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.address_repo = AddressRepository(db)
        self.product_repo = ProductRepository(db)
        self.cart_repo = CartRepository()

    async def create_order(self, user_id: str, data: OrderCreate) -> Order:
        # 1. Fetch user cart
        cart = await self.cart_repo.get_cart_by_user_id(user_id)
        items = cart.get("items", [])
        if not items:
            raise BadRequestError("Cannot place an order with an empty shopping cart")

        # 2. Verify Shipping Address
        address = await self.address_repo.get_by_id(data.address_id)
        if not address or address.user_id != user_id:
            raise NotFoundError("Shipping Address")

        total_amount = 0.0
        order_items = []

        # 3. Reserve stock and compute totals
        for item in items:
            product_id = item["product_id"]
            qty = int(item["quantity"])
            product = await self.product_repo.get_by_id(product_id)
            if not product or not product.is_active:
                raise BadRequestError(f"Product {item.get('title')} is no longer available")

            if not product.inventory or product.inventory.quantity < qty:
                raise InsufficientStockError(product.title)

            # Deduct stock
            product.inventory.quantity -= qty
            product.inventory.reserved_quantity += qty

            item_price = round(product.price * (1 - product.discount_percentage / 100.0), 2)
            item_total = round(item_price * qty, 2)
            total_amount += item_total

            order_items.append(OrderItem(
                product_id=product.id,
                product_name=product.title,
                unit_price=item_price,
                quantity=qty,
                total_price=item_total
            ))

        discount_amount = 0.0
        if data.coupon_code == "WELCOME10":
            discount_amount = round(total_amount * 0.10, 2)

        final_amount = round(total_amount - discount_amount, 2)
        order_number = f"AMZ-{random.randint(100000, 999999)}"

        order = Order(
            order_number=order_number,
            user_id=user_id,
            address_id=address.id,
            status="pending",
            total_amount=total_amount,
            discount_amount=discount_amount,
            final_amount=final_amount,
            items=order_items
        )
        await self.order_repo.create(order)

        # 4. Clear cart after successful order creation
        await self.cart_repo.clear_cart(user_id)

        return order

    async def get_user_orders(self, user_id: str) -> List[Order]:
        return await self.order_repo.get_user_orders(user_id)

    async def get_order_details(self, order_id: str, user_id: Optional[str] = None) -> Order:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundError("Order")
        if user_id and order.user_id != user_id:
            raise NotFoundError("Order")
        return order

    async def update_order_status(self, order_id: str, new_status: str) -> Order:
        order = await self.get_order_details(order_id)
        order.status = new_status
        await self.order_repo.update(order)
        return order

    async def cancel_order(self, order_id: str, user_id: str) -> Order:
        order = await self.get_order_details(order_id, user_id)
        if order.status in ["shipped", "delivered", "cancelled"]:
            raise BadRequestError(f"Cannot cancel order in status '{order.status}'")
        order.status = "cancelled"
        
        # Restore inventory
        for item in order.items:
            product = await self.product_repo.get_by_id(item.product_id)
            if product and product.inventory:
                product.inventory.quantity += item.quantity
                if product.inventory.reserved_quantity >= item.quantity:
                    product.inventory.reserved_quantity -= item.quantity

        await self.order_repo.update(order)
        return order

    async def track_order(self, order_id: str, user_id: str) -> Dict[str, Any]:
        order = await self.get_order_details(order_id, user_id)
        statuses = ["pending", "processing", "shipped", "delivered"]
        current_idx = statuses.index(order.status) if order.status in statuses else 0
        
        timeline = []
        for idx, st in enumerate(statuses):
            timeline.append({
                "status": st.upper(),
                "completed": idx <= current_idx,
                "current": idx == current_idx
            })

        return {
            "order_number": order.order_number,
            "current_status": order.status,
            "tracking_number": f"TRK-{uuid.uuid4().hex[:8].upper()}",
            "estimated_delivery": "3-5 Business Days",
            "timeline": timeline
        }
