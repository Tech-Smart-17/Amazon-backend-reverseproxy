"""
Notification Feed Endpoints (/api/v1/notifications).
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from app.services.notification_service import NotificationService
from app.dependencies import get_notification_service, get_current_user
from app.models.sql_models import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("")
async def get_notifications(
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    return await notification_service.get_user_notifications(current_user.id, unread_only)

@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    await notification_service.mark_as_read(notification_id, current_user.id)
    return {"success": True, "message": "Notification marked as read"}
