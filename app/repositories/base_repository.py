"""
Generic Base SQL Repository for standard CRUD operations using SQLAlchemy Async.
"""
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id_val: str) -> Optional[ModelType]:
        result = await self.db.execute(select(self.model).filter(self.model.id == id_val))
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        result = await self.db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        await self.db.flush()
        return obj

    async def update(self, obj: ModelType) -> ModelType:
        await self.db.flush()
        return obj

    async def delete(self, obj: ModelType) -> bool:
        await self.db.delete(obj)
        await self.db.flush()
        return True
