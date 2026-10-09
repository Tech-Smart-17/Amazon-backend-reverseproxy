"""
MongoDB Notification & Audit Repository.
"""
from typing import List, Dict, Any
import uuid
from datetime import datetime, timezone
from app.database import get_mongo_db

class NotificationRepository:
    def __init__(self):
        self.db = get_mongo_db()
        self.collection = self.db.get_collection("notifications")

    async def create_notification(self, user_id: str, title: str, message: str, type_str: str = "system") -> Dict[str, Any]:
        doc = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": type_str,
            "is_read": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await self.collection.insert_one(doc)
        return doc

    async def get_user_notifications(self, user_id: str, unread_only: bool = False) -> List[Dict[str, Any]]:
        query = {"user_id": user_id}
        if unread_only:
            query["is_read"] = False
        cursor = self.collection.find(query).sort("created_at", -1)
        results = await cursor.to_list(length=50)
        return results

    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        res = await self.collection.update_one(
            {"_id": notification_id, "user_id": user_id},
            {"$set": {"is_read": True}}
        )
        return res.modified_count > 0
