"""
Wishlist Endpoints (/api/v1/wishlist).
"""
from fastapi import APIRouter, Depends, status
from app.schemas.all_schemas import WishlistAdd, CartResponse
from app.services.wishlist_service import WishlistService
from app.dependencies import get_wishlist_service, get_current_user
from app.models.sql_models import User

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])

@router.get("")
async def get_wishlist(
    current_user: User = Depends(get_current_user),
    wishlist_service: WishlistService = Depends(get_wishlist_service)
):
    return await wishlist_service.get_wishlist(current_user.id)

@router.post("/items")
async def add_to_wishlist(
    data: WishlistAdd,
    current_user: User = Depends(get_current_user),
    wishlist_service: WishlistService = Depends(get_wishlist_service)
):
    return await wishlist_service.add_to_wishlist(current_user.id, data.product_id)

@router.delete("/items/{product_id}")
async def remove_from_wishlist(
    product_id: str,
    current_user: User = Depends(get_current_user),
    wishlist_service: WishlistService = Depends(get_wishlist_service)
):
    return await wishlist_service.remove_from_wishlist(current_user.id, product_id)

@router.post("/items/{product_id}/move-to-cart", response_model=CartResponse)
async def move_to_cart(
    product_id: str,
    current_user: User = Depends(get_current_user),
    wishlist_service: WishlistService = Depends(get_wishlist_service)
):
    return await wishlist_service.move_to_cart(current_user.id, product_id)
