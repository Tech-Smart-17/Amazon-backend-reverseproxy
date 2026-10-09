"""
Order Management & Tracking Endpoints (/api/v1/orders).
"""
from typing import List
from fastapi import APIRouter, Depends, status
from app.schemas.all_schemas import OrderCreate, OrderResponse
from app.services.order_service import OrderService
from app.dependencies import get_order_service, get_current_user, require_roles
from app.models.sql_models import User

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    data: OrderCreate,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    return await order_service.create_order(current_user.id, data)

@router.get("", response_model=List[OrderResponse])
async def list_my_orders(
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    return await order_service.get_user_orders(current_user.id)

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_details(
    order_id: str,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    return await order_service.get_order_details(order_id, current_user.id)

@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    return await order_service.cancel_order(order_id, current_user.id)

@router.get("/{order_id}/track")
async def track_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    return await order_service.track_order(order_id, current_user.id)

@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    status_name: str,
    current_user: User = Depends(require_roles(["admin", "manager"])),
    order_service: OrderService = Depends(get_order_service)
):
    return await order_service.update_order_status(order_id, status_name)
