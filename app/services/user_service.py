"""
User Profile Management Service.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.models.sql_models import User
from app.schemas.all_schemas import UserUpdate, ChangePasswordSchema
from app.security import hash_password, verify_password
from app.exceptions import NotFoundError, BadRequestError

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def get_profile(self, user_id: str) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User")
        return user

    async def update_profile(self, user_id: str, data: UserUpdate) -> User:
        user = await self.get_profile(user_id)
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.phone_number is not None:
            user.phone_number = data.phone_number
        await self.user_repo.update(user)
        return user

    async def update_avatar(self, user_id: str, avatar_url: str) -> User:
        user = await self.get_profile(user_id)
        user.avatar_url = avatar_url
        await self.user_repo.update(user)
        return user

    async def change_password(self, user_id: str, data: ChangePasswordSchema) -> bool:
        user = await self.get_profile(user_id)
        if not verify_password(data.current_password, user.hashed_password):
            raise BadRequestError("Current password incorrect")
        user.hashed_password = hash_password(data.new_password)
        await self.user_repo.update(user)
        return True

    async def deactivate_account(self, user_id: str) -> bool:
        user = await self.get_profile(user_id)
        user.is_active = False
        await self.user_repo.update(user)
        return True
