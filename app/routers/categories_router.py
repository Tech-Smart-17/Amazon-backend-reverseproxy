"""
Category Management Endpoints (/api/v1/categories).
"""
from typing import List
from fastapi import APIRouter, Depends, status
from app.schemas.all_schemas import CategoryCreate, CategoryResponse
from app.services.product_service import ProductService
from app.dependencies import get_product_service, require_roles
from app.models.sql_models import User

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("", response_model=List[CategoryResponse])
async def list_categories(product_service: ProductService = Depends(get_product_service)):
    return await product_service.get_all_categories()

@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    current_user: User = Depends(require_roles(["admin", "manager"])),
    product_service: ProductService = Depends(get_product_service)
):
    return await product_service.create_category(data)
