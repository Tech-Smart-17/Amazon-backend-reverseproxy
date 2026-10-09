"""
Inventory & Stock Management Endpoints (/api/v1/inventory).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.sql_models import Inventory, Product, User
from app.schemas.all_schemas import InventoryUpdate, InventoryResponse
from app.dependencies import require_roles
from app.exceptions import NotFoundError

router = APIRouter(prefix="/inventory", tags=["Inventory Management"])

@router.get("/{product_id}", response_model=InventoryResponse)
async def get_inventory(product_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Inventory).filter(Inventory.product_id == product_id))
    inv = result.scalars().first()
    if not inv:
        raise NotFoundError("Inventory for product")
    return inv

@router.put("/{product_id}", response_model=InventoryResponse)
async def update_inventory(
    product_id: str,
    data: InventoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "manager", "vendor"]))
):
    result = await db.execute(select(Inventory).filter(Inventory.product_id == product_id))
    inv = result.scalars().first()
    if not inv:
        inv = Inventory(product_id=product_id)
        db.add(inv)

    inv.quantity = data.quantity
    if data.warehouse_id is not None:
        inv.warehouse_id = data.warehouse_id
    if data.low_stock_threshold is not None:
        inv.low_stock_threshold = data.low_stock_threshold

    await db.flush()
    return inv
