"""
Analytics & Admin Management Services.
"""
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.user_repository import UserRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.order_repository import OrderRepository
from app.models.sql_models import Warehouse, Inventory
from app.schemas.all_schemas import WarehouseCreate

class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.analytics_repo = AnalyticsRepository(db)

    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        return await self.analytics_repo.get_dashboard_metrics()

class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.product_repo = ProductRepository(db)
        self.order_repo = OrderRepository(db)

    async def create_warehouse(self, data: WarehouseCreate) -> Warehouse:
        warehouse = Warehouse(
            name=data.name,
            code=data.code,
            location=data.location,
            capacity=data.capacity
        )
        self.db.add(warehouse)
        await self.db.flush()
        return warehouse

    async def list_users(self, skip: int = 0, limit: int = 50) -> List[Any]:
        return await self.user_repo.get_all(skip=skip, limit=limit)
