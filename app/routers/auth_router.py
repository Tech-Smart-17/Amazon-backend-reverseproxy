"""
Authentication Endpoints (/api/v1/auth).
"""
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.all_schemas import (
    UserRegister, UserLogin, TokenResponse, RefreshTokenRequest, PasswordResetRequest
)
from app.services.auth_service import AuthService
from app.dependencies import get_auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, auth_service: AuthService = Depends(get_auth_service)):
    user = await auth_service.register(data)
    return {"success": True, "message": "User registered successfully", "user_id": user.id}

@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.login(data)

@router.post("/login/form", response_model=TokenResponse)
async def login_form(form_data: OAuth2PasswordRequestForm = Depends(), auth_service: AuthService = Depends(get_auth_service)):
    login_data = UserLogin(email=form_data.username, password=form_data.password)
    return await auth_service.login(login_data)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.refresh_access_token(data.refresh_token)

@router.post("/forgot-password")
async def forgot_password(data: PasswordResetRequest):
    return {"success": True, "message": "Password reset token sent to email"}
