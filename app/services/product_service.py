"""
Product & Category Management Service.
"""
from typing import List, Optional
import asyncio
import logging
import re
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.product_repository import ProductRepository, CategoryRepository
from app.repositories.search_repository import SearchRepository
from app.models.sql_models import Product, Category, Inventory
from app.schemas.all_schemas import ProductCreate, ProductUpdate, CategoryCreate
from app.exceptions import NotFoundError, BadRequestError

logger = logging.getLogger("amazon_backend.products")

def slugify(text: str) -> str:
    text = text.lower().strip()
    return re.sub(r'[^\w\s-]', '', text).replace(' ', '-').replace('--', '-')

class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.product_repo = ProductRepository(db)
        self.category_repo = CategoryRepository(db)
        self.search_repo = SearchRepository()

    async def create_category(self, data: CategoryCreate) -> Category:
        slug = slugify(data.name)
        existing = await self.category_repo.get_by_slug(slug)
        if existing:
            raise BadRequestError("Category with this name already exists")
        category = Category(
            name=data.name,
            slug=slug,
            description=data.description,
            parent_id=data.parent_id
        )
        await self.category_repo.create(category)
        return category

    async def get_all_categories(self) -> List[Category]:
        return await self.category_repo.get_all()


    async def create_product(self, data: ProductCreate) -> Product:
        existing = await self.product_repo.get_by_sku(data.sku)
        if existing:
            raise BadRequestError("Product with this SKU already exists")

        slug = slugify(data.title)
        product = Product(
            sku=data.sku,
            title=data.title,
            slug=slug,
            description=data.description,
            brand=data.brand,
            price=data.price,
            discount_percentage=data.discount_percentage,
            category_id=data.category_id
        )
        await self.product_repo.create(product)

        # Initialize stock inventory
        inventory = Inventory(
            product_id=product.id,
            quantity=data.stock_quantity
        )
        self.db.add(inventory)
        await self.db.flush()

        # Index into ChromaDB vector store
        category_name = ""
        if data.category_id:
            cat = await self.category_repo.get_by_id(data.category_id)
            if cat:
                category_name = cat.name
        try:
            await asyncio.to_thread(
                self.search_repo.index_product,
                product.id,
                product.title,
                product.description,
                product.brand,
                category_name,
            )
        except Exception:
            logger.exception("Could not index product %s; SQL search remains available", product.id)

        return product

    async def get_product_by_id(self, product_id: str) -> Product:
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundError("Product")
        return product

    async def list_products(
        self,
        category_id: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        search_query: Optional[str] = None,
        sort_by: Optional[str] = "created_at",
        skip: int = 0,
        limit: int = 20
    ) -> List[dict]:
        products = await self.product_repo.filter_products(
            category_id=category_id,
            brand=brand,
            min_price=min_price,
            max_price=max_price,
            search_query=search_query,
            sort_by=sort_by,
            skip=skip,
            limit=limit
        )
        res = []
        for p in products:
            final_p = round(p.price * (1 - p.discount_percentage / 100.0), 2)
            stock_qty = p.inventory.quantity if p.inventory else 0
            res.append({
                "id": p.id,
                "sku": p.sku,
                "title": p.title,
                "slug": p.slug,
                "description": p.description,
                "brand": p.brand,
                "price": p.price,
                "discount_percentage": p.discount_percentage,
                "final_price": final_p,
                "category_id": p.category_id,
                "is_active": p.is_active,
                "stock_quantity": stock_qty,
                "created_at": p.created_at
            })
        return res

    async def update_product(self, product_id: str, data: ProductUpdate) -> Product:
        product = await self.get_product_by_id(product_id)
        if data.title is not None:
            product.title = data.title
            product.slug = slugify(data.title)
        if data.description is not None:
            product.description = data.description
        if data.brand is not None:
            product.brand = data.brand
        if data.price is not None:
            product.price = data.price
        if data.discount_percentage is not None:
            product.discount_percentage = data.discount_percentage
        if data.category_id is not None:
            product.category_id = data.category_id
        if data.is_active is not None:
            product.is_active = data.is_active

        await self.product_repo.update(product)

        category_name = ""
        if product.category_id:
            category = await self.category_repo.get_by_id(product.category_id)
            if category:
                category_name = category.name
        if product.is_active:
            # Re-index all searchable fields after an update.
            try:
                await asyncio.to_thread(
                    self.search_repo.index_product,
                    product.id,
                    product.title,
                    product.description,
                    product.brand,
                    category_name,
                )
            except Exception:
                logger.exception("Could not re-index product %s", product.id)
        else:
            try:
                await asyncio.to_thread(self.search_repo.delete_product, product.id)
            except Exception:
                logger.exception("Could not remove inactive product %s from the vector index", product.id)
        return product

    async def delete_product(self, product_id: str) -> bool:
        product = await self.get_product_by_id(product_id)
        deleted = await self.product_repo.delete(product)
        try:
            await asyncio.to_thread(self.search_repo.delete_product, product_id)
        except Exception:
            logger.exception("Could not remove deleted product %s from the vector index", product_id)
        return deleted
