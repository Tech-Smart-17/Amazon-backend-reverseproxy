"""
Wishlist Service with Move-to-Cart capability.
"""
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.wishlist_repository import WishlistRepository
from app.services.cart_service import CartService
from app.repositories.product_repository import ProductRepository
from app.exceptions import NotFoundError

class WishlistService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.wishlist_repo = WishlistRepository()
        self.cart_service = CartService(db)
        self.product_repo = ProductRepository(db)

    async def get_wishlist(self, user_id: str) -> Dict[str, Any]:
        return await self.wishlist_repo.get_wishlist(user_id)

    async def add_to_wishlist(self, user_id: str, product_id: str) -> Dict[str, Any]:
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundError("Product")
        return await self.wishlist_repo.add_item(user_id, product_id)

    async def remove_from_wishlist(self, user_id: str, product_id: str) -> Dict[str, Any]:
        return await self.wishlist_repo.remove_item(user_id, product_id)

    async def move_to_cart(self, user_id: str, product_id: str) -> Dict[str, Any]:
        await self.cart_service.add_to_cart(user_id, product_id, quantity=1)
        await self.wishlist_repo.remove_item(user_id, product_id)
        return await self.cart_service.get_cart(user_id)
