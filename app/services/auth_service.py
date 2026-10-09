"""
Authentication Service handling user registration, token generation, and password resets.
"""
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.models.sql_models import User, Role
from app.schemas.all_schemas import UserRegister, UserLogin
from app.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.exceptions import UnauthorizedError, BadRequestError

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, data: UserRegister) -> User:
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise BadRequestError("Email address is already registered")

        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            phone_number=data.phone_number
        )
        await self.user_repo.create(user)

        role_name = data.role or "customer"
        role = await self.user_repo.get_role_by_name(role_name)
        if role:
            await self.user_repo.assign_role(user.id, role.id)

        return user

    async def login(self, data: UserLogin) -> Dict[str, str]:
        user = await self.user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedError("User account is deactivated")

        roles = [r.name for r in user.roles]
        token_data = {"sub": user.id, "email": user.email, "roles": roles}
        
        return {
            "access_token": create_access_token(token_data),
            "refresh_token": create_refresh_token(token_data),
            "token_type": "bearer"
        }

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid refresh token type")
        
        user_id = payload.get("sub")
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedError("User invalid or inactive")

        roles = [r.name for r in user.roles]
        token_data = {"sub": user.id, "email": user.email, "roles": roles}

        return {
            "access_token": create_access_token(token_data),
            "refresh_token": create_refresh_token(token_data),
            "token_type": "bearer"
        }
