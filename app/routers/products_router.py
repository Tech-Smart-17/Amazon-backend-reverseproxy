"""
Product Catalog Endpoints (/api/v1/products).
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from app.schemas.all_schemas import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import ProductService
from app.dependencies import get_product_service, require_roles
from app.models.sql_models import User

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=List[ProductResponse])
async def list_products(
    category_id: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    skip: int = 0,
    limit: int = 20,
    product_service: ProductService = Depends(get_product_service)
):
    return await product_service.list_products(
        category_id=category_id,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        search_query=search,
        sort_by=sort_by,
        skip=skip,
        limit=limit
    )

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, product_service: ProductService = Depends(get_product_service)):
    p = await product_service.get_product_by_id(product_id)
    final_p = round(p.price * (1 - p.discount_percentage / 100.0), 2)
    stock_qty = p.inventory.quantity if p.inventory else 0
    return ProductResponse(
        id=p.id,
        sku=p.sku,
        title=p.title,
        slug=p.slug,
        description=p.description,
        brand=p.brand,
        price=p.price,
        discount_percentage=p.discount_percentage,
        final_price=final_p,
        category_id=p.category_id,
        is_active=p.is_active,
        stock_quantity=stock_qty,
        created_at=p.created_at
    )

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    current_user: User = Depends(require_roles(["admin", "vendor", "manager"])),
    product_service: ProductService = Depends(get_product_service)
):
    p = await product_service.create_product(data)
    final_p = round(p.price * (1 - p.discount_percentage / 100.0), 2)
    return ProductResponse(
        id=p.id,
        sku=p.sku,
        title=p.title,
        slug=p.slug,
        description=p.description,
        brand=p.brand,
        price=p.price,
        discount_percentage=p.discount_percentage,
        final_price=final_p,
        category_id=p.category_id,
        is_active=p.is_active,
        stock_quantity=data.stock_quantity,
        created_at=p.created_at
    )

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    data: ProductUpdate,
    current_user: User = Depends(require_roles(["admin", "vendor", "manager"])),
    product_service: ProductService = Depends(get_product_service)
):
    p = await product_service.update_product(product_id, data)
    final_p = round(p.price * (1 - p.discount_percentage / 100.0), 2)
    stock_qty = p.inventory.quantity if p.inventory else 0
    return ProductResponse(
        id=p.id,
        sku=p.sku,
        title=p.title,
        slug=p.slug,
        description=p.description,
        brand=p.brand,
        price=p.price,
        discount_percentage=p.discount_percentage,
        final_price=final_p,
        category_id=p.category_id,
        is_active=p.is_active,
        stock_quantity=stock_qty,
        created_at=p.created_at
    )

@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    current_user: User = Depends(require_roles(["admin", "manager"])),
    product_service: ProductService = Depends(get_product_service)
):
    await product_service.delete_product(product_id)
    return {"success": True, "message": "Product deleted"}
