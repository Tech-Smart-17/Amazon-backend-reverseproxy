"""
User Address Management Endpoints (/api/v1/address).
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.all_schemas import AddressCreate, AddressResponse
from app.repositories.order_repository import AddressRepository
from app.models.sql_models import Address, User
from app.dependencies import get_current_user
from app.exceptions import NotFoundError

router = APIRouter(prefix="/address", tags=["Address Management"])

@router.get("", response_model=List[AddressResponse])
async def list_addresses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = AddressRepository(db)
    return await repo.get_user_addresses(current_user.id)

@router.post("", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
async def create_address(
    data: AddressCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = AddressRepository(db)
    addr = Address(
        user_id=current_user.id,
        full_name=data.full_name,
        street_address=data.street_address,
        city=data.city,
        state=data.state,
        postal_code=data.postal_code,
        country=data.country,
        phone=data.phone,
        is_default=data.is_default
    )
    await repo.create(addr)
    return addr

@router.delete("/{address_id}")
async def delete_address(
    address_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = AddressRepository(db)
    addr = await repo.get_by_id(address_id)
    if not addr or addr.user_id != current_user.id:
        raise NotFoundError("Address")
    await repo.delete(addr)
    return {"success": True, "message": "Address deleted"}
