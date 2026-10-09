"""
User Data Access Repository.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.repositories.base_repository import BaseRepository
from app.models.sql_models import User, Role, UserRoleMap

class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def get_role_by_name(self, role_name: str) -> Optional[Role]:
        result = await self.db.execute(select(Role).filter(Role.name == role_name))
        return result.scalars().first()

    async def assign_role(self, user_id: str, role_id: str):
        mapping = UserRoleMap(user_id=user_id, role_id=role_id)
        self.db.add(mapping)
        await self.db.flush()
