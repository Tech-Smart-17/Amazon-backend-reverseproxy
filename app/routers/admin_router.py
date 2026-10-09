"""
Admin Control Center Endpoints (/api/v1/admin).
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from app.services.analytics_service import AdminService
from app.dependencies import get_admin_service, require_roles
from app.models.sql_models import User
from app.schemas.all_schemas import UserProfileResponse

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

@router.get("/users", response_model=List[UserProfileResponse])
async def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_roles(["admin"])),
    admin_service: AdminService = Depends(get_admin_service)
):
    users = await admin_service.list_users(skip=skip, limit=limit)
    res = []
    for u in users:
        roles = [r.name for r in u.roles]
        res.append(UserProfileResponse(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            phone_number=u.phone_number,
            avatar_url=u.avatar_url,
            is_active=u.is_active,
            is_verified=u.is_verified,
            roles=roles,
            created_at=u.created_at
        ))
    return res
