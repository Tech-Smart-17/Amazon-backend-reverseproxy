"""
Product and Category Data Access Repository.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from app.repositories.base_repository import BaseRepository
from app.models.sql_models import Product, Category, Inventory

class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: AsyncSession):
        super().__init__(Product, db)

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        result = await self.db.execute(select(Product).filter(Product.sku == sku))
        return result.scalars().first()

    async def get_by_slug(self, slug: str) -> Optional[Product]:
        result = await self.db.execute(select(Product).filter(Product.slug == slug))
        return result.scalars().first()

    async def filter_products(
        self,
        category_id: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        search_query: Optional[str] = None,
        sort_by: Optional[str] = "created_at",
        skip: int = 0,
        limit: int = 20
    ) -> List[Product]:
        query = select(Product).filter(Product.is_active == True)

        if category_id:
            query = query.filter(Product.category_id == category_id)
        if brand:
            query = query.filter(Product.brand.ilike(f"%{brand}%"))
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        if search_query:
            query = query.filter(
                or_(
                    Product.title.ilike(f"%{search_query}%"),
                    Product.description.ilike(f"%{search_query}%"),
                    Product.brand.ilike(f"%{search_query}%")
                )
            )

        if sort_by == "price_asc":
            query = query.order_by(Product.price.asc())
        elif sort_by == "price_desc":
            query = query.order_by(Product.price.desc())
        else:
            query = query.order_by(Product.created_at.desc())

        result = await self.db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: AsyncSession):
        super().__init__(Category, db)

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        result = await self.db.execute(select(Category).filter(Category.slug == slug))
        return result.scalars().first()
