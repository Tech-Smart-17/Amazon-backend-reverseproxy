"""
MongoDB Cart Repository for User Shopping Cart operations.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from app.database import get_mongo_db

class CartRepository:
    def __init__(self):
        self.db = get_mongo_db()
        self.collection = self.db.get_collection("carts")

    async def get_cart_by_user_id(self, user_id: str) -> Dict[str, Any]:
        cart = await self.collection.find_one({"user_id": user_id})
        if not cart:
            cart = {
                "user_id": user_id,
                "items": [],
                "updated_at": datetime.now(timezone.utc)
            }
            await self.collection.insert_one(cart)
        return cart

    async def add_or_update_item(self, user_id: str, product_id: str, quantity: int, price: float, title: str) -> Dict[str, Any]:
        cart = await self.get_cart_by_user_id(user_id)
        items = cart.get("items", [])
        
        found = False
        for item in items:
            if item.get("product_id") == product_id:
                item["quantity"] += quantity
                item["price"] = price
                item["title"] = title
                found = True
                break

        if not found:
            items.append({
                "product_id": product_id,
                "quantity": quantity,
                "price": price,
                "title": title
            })

        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"items": items, "updated_at": datetime.now(timezone.utc)}}
        )
        return await self.get_cart_by_user_id(user_id)

    async def remove_item(self, user_id: str, product_id: str) -> Dict[str, Any]:
        cart = await self.get_cart_by_user_id(user_id)
        items = [i for i in cart.get("items", []) if i.get("product_id") != product_id]
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"items": items, "updated_at": datetime.now(timezone.utc)}}
        )
        return await self.get_cart_by_user_id(user_id)

    async def clear_cart(self, user_id: str) -> bool:
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"items": [], "updated_at": datetime.now(timezone.utc)}}
        )
        return True
