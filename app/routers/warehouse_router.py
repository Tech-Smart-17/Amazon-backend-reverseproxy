"""
Warehouse Management Endpoints (/api/v1/warehouse).
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.sql_models import Warehouse, User
from app.schemas.all_schemas import WarehouseCreate, WarehouseResponse
from app.dependencies import require_roles, get_admin_service
from app.services.analytics_service import AdminService

router = APIRouter(prefix="/warehouse", tags=["Warehouse"])

@router.get("", response_model=List[WarehouseResponse])
async def list_warehouses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Warehouse))
    return result.scalars().all()

@router.post("", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    data: WarehouseCreate,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(require_roles(["admin"]))
):
    return await admin_service.create_warehouse(data)
