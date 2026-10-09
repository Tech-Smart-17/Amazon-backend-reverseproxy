"""
User Profile Management Endpoints (/api/v1/users).
"""
from fastapi import APIRouter, Depends, UploadFile, File, status
from app.schemas.all_schemas import UserProfileResponse, UserUpdate, ChangePasswordSchema
from app.services.user_service import UserService
from app.dependencies import get_user_service, get_current_user
from app.models.sql_models import User
from app.utils import save_uploaded_file

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    roles = [r.name for r in current_user.roles]
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone_number=current_user.phone_number,
        avatar_url=current_user.avatar_url,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        roles=roles,
        created_at=current_user.created_at
    )

@router.put("/me", response_model=UserProfileResponse)
async def update_my_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    updated = await user_service.update_profile(current_user.id, data)
    roles = [r.name for r in updated.roles]
    return UserProfileResponse(
        id=updated.id,
        email=updated.email,
        full_name=updated.full_name,
        phone_number=updated.phone_number,
        avatar_url=updated.avatar_url,
        is_active=updated.is_active,
        is_verified=updated.is_verified,
        roles=roles,
        created_at=updated.created_at
    )

@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    content = await file.read()
    avatar_url = save_uploaded_file(content, file.filename, subfolder="profile_images")
    await user_service.update_avatar(current_user.id, avatar_url)
    return {"success": True, "avatar_url": avatar_url}

@router.post("/me/change-password")
async def change_password(
    data: ChangePasswordSchema,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    await user_service.change_password(current_user.id, data)
    return {"success": True, "message": "Password changed successfully"}

@router.post("/me/deactivate")
async def deactivate_account(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    await user_service.deactivate_account(current_user.id)
    return {"success": True, "message": "Account deactivated"}
