"""
Shopping Cart Service handling MongoDB cart state, stock validation, and pricing.
"""
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.exceptions import NotFoundError, InsufficientStockError

class CartService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cart_repo = CartRepository()
        self.product_repo = ProductRepository(db)

    async def get_cart(self, user_id: str) -> Dict[str, Any]:
        cart = await self.cart_repo.get_cart_by_user_id(user_id)
        total = 0.0
        items = cart.get("items", [])
        for item in items:
            total += float(item.get("price", 0.0)) * int(item.get("quantity", 1))
        
        return {
            "user_id": user_id,
            "items": items,
            "total_amount": round(total, 2)
        }

    async def add_to_cart(self, user_id: str, product_id: str, quantity: int) -> Dict[str, Any]:
        product = await self.product_repo.get_by_id(product_id)
        if not product or not product.is_active:
            raise NotFoundError("Product")

        available_stock = product.inventory.quantity if product.inventory else 0
        if available_stock < quantity:
            raise InsufficientStockError(product.title)

        final_price = round(product.price * (1 - product.discount_percentage / 100.0), 2)
        await self.cart_repo.add_or_update_item(
            user_id=user_id,
            product_id=product.id,
            quantity=quantity,
            price=final_price,
            title=product.title
        )
        return await self.get_cart(user_id)

    async def update_item_quantity(self, user_id: str, product_id: str, quantity: int) -> Dict[str, Any]:
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundError("Product")

        available_stock = product.inventory.quantity if product.inventory else 0
        if available_stock < quantity:
            raise InsufficientStockError(product.title)

        final_price = round(product.price * (1 - product.discount_percentage / 100.0), 2)
        # Clear item first, then re-add exact quantity
        await self.cart_repo.remove_item(user_id, product_id)
        await self.cart_repo.add_or_update_item(
            user_id=user_id,
            product_id=product.id,
            quantity=quantity,
            price=final_price,
            title=product.title
        )
        return await self.get_cart(user_id)

    async def remove_from_cart(self, user_id: str, product_id: str) -> Dict[str, Any]:
        await self.cart_repo.remove_item(user_id, product_id)
        return await self.get_cart(user_id)

    async def clear_cart(self, user_id: str) -> bool:
        return await self.cart_repo.clear_cart(user_id)
