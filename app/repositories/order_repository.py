"""
Order and Address Data Access Repository.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.repositories.base_repository import BaseRepository
from app.models.sql_models import Order, OrderItem, Address, Payment, Invoice

class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: AsyncSession):
        super().__init__(Order, db)

    async def get_by_order_number(self, order_number: str) -> Optional[Order]:
        result = await self.db.execute(select(Order).filter(Order.order_number == order_number))
        return result.scalars().first()

    async def get_user_orders(self, user_id: str, skip: int = 0, limit: int = 20) -> List[Order]:
        result = await self.db.execute(
            select(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all()

class AddressRepository(BaseRepository[Address]):
    def __init__(self, db: AsyncSession):
        super().__init__(Address, db)

    async def get_user_addresses(self, user_id: str) -> List[Address]:
        result = await self.db.execute(select(Address).filter(Address.user_id == user_id))
        return result.scalars().all()
