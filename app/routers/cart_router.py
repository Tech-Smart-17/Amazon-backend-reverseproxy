"""
Shopping Cart Endpoints (/api/v1/cart).
"""
from fastapi import APIRouter, Depends, status
from app.schemas.all_schemas import CartItemAdd, CartItemUpdate, CartResponse
from app.services.cart_service import CartService
from app.dependencies import get_cart_service, get_current_user
from app.models.sql_models import User

router = APIRouter(prefix="/cart", tags=["Shopping Cart"])

@router.get("", response_model=CartResponse)
async def get_cart(
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
):
    return await cart_service.get_cart(current_user.id)

@router.post("/items", response_model=CartResponse)
async def add_item_to_cart(
    data: CartItemAdd,
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
):
    return await cart_service.add_to_cart(current_user.id, data.product_id, data.quantity)

@router.put("/items/{product_id}", response_model=CartResponse)
async def update_cart_item(
    product_id: str,
    data: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
):
    return await cart_service.update_item_quantity(current_user.id, product_id, data.quantity)

@router.delete("/items/{product_id}", response_model=CartResponse)
async def delete_cart_item(
    product_id: str,
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
):
    return await cart_service.remove_from_cart(current_user.id, product_id)

@router.delete("")
async def clear_cart(
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
):
    await cart_service.clear_cart(current_user.id)
    return {"success": True, "message": "Shopping cart cleared"}
