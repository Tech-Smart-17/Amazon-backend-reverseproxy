"""
Notification Delivery & Management Service.
"""
from typing import List, Dict, Any
from app.repositories.notification_repository import NotificationRepository

class NotificationService:
    def __init__(self):
        self.notification_repo = NotificationRepository()

    async def send_notification(self, user_id: str, title: str, message: str, type_str: str = "system") -> Dict[str, Any]:
        return await self.notification_repo.create_notification(user_id, title, message, type_str)

    async def get_user_notifications(self, user_id: str, unread_only: bool = False) -> List[Dict[str, Any]]:
        return await self.notification_repo.get_user_notifications(user_id, unread_only)

    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        return await self.notification_repo.mark_as_read(notification_id, user_id)
