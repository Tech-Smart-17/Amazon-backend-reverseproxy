"""
MongoDB Wishlist Repository for User Wishlist operations.
"""
from typing import Dict, Any, List
from datetime import datetime, timezone
from app.database import get_mongo_db

class WishlistRepository:
    def __init__(self):
        self.db = get_mongo_db()
        self.collection = self.db.get_collection("wishlists")

    async def get_wishlist(self, user_id: str) -> Dict[str, Any]:
        wishlist = await self.collection.find_one({"user_id": user_id})
        if not wishlist:
            wishlist = {"user_id": user_id, "items": []}
            await self.collection.insert_one(wishlist)
        return wishlist

    async def add_item(self, user_id: str, product_id: str) -> Dict[str, Any]:
        wishlist = await self.get_wishlist(user_id)
        items = wishlist.get("items", [])
        if not any(i.get("product_id") == product_id for i in items):
            items.append({
                "product_id": product_id,
                "added_at": datetime.now(timezone.utc).isoformat()
            })
            await self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"items": items}}
            )
        return await self.get_wishlist(user_id)

    async def remove_item(self, user_id: str, product_id: str) -> Dict[str, Any]:
        wishlist = await self.get_wishlist(user_id)
        items = [i for i in wishlist.get("items", []) if i.get("product_id") != product_id]
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"items": items}}
        )
        return await self.get_wishlist(user_id)
