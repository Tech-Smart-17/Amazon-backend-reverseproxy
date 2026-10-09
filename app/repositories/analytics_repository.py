"""
Analytics Data Repository using SQLAlchemy queries.
"""
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.sql_models import User, Product, Order, Inventory

class AnalyticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        users_count = (await self.db.execute(select(func.count(User.id)))).scalar() or 0
        products_count = (await self.db.execute(select(func.count(Product.id)))).scalar() or 0
        orders_count = (await self.db.execute(select(func.count(Order.id)))).scalar() or 0
        revenue = (await self.db.execute(select(func.sum(Order.final_amount)).filter(Order.status == "delivered"))).scalar() or 0.0
        low_stock = (await self.db.execute(select(func.count(Inventory.id)).filter(Inventory.quantity <= Inventory.low_stock_threshold))).scalar() or 0

        return {
            "total_users": users_count,
            "total_products": products_count,
            "total_orders": orders_count,
            "total_revenue": round(float(revenue), 2),
            "low_stock_products_count": low_stock
        }
