"""Rebuild the LangChain product index from the current SQL catalog."""
import asyncio

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.sql_models import Category, Product
from app.repositories.search_repository import SearchRepository


async def main() -> None:
    search_repository = SearchRepository()
    statement = (
        select(
            Product.id,
            Product.title,
            Product.description,
            Product.brand,
            Category.name,
        )
        .outerjoin(Category, Product.category_id == Category.id)
        .where(Product.is_active.is_(True))
    )
    async with AsyncSessionLocal() as session:
        rows = (await session.execute(statement)).all()
        for product_id, title, description, brand, category in rows:
            search_repository.index_product(
                product_id,
                title,
                description or "",
                brand or "",
                category or "",
            )
    print(f"Indexed {len(rows)} active products.")


if __name__ == "__main__":
    asyncio.run(main())
