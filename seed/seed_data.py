"""
Database Seeding Script for Amazon Backend System.
Inserts default Roles, Admin User, Sample Categories, Products, Inventory, Warehouses, and ChromaDB Vector Embeddings.
"""
import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import AsyncSessionLocal, engine, Base
from app.models.sql_models import User, Role, Category, Product, Inventory, Warehouse, UserRoleMap
from app.security import hash_password
from app.repositories.search_repository import SearchRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_script")

async def seed():
    logger.info("Starting database seeding process...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Create Roles
        role_names = ["admin", "customer", "vendor", "manager"]
        roles_dict = {}
        for r_name in role_names:
            res = await session.execute(select(Role).filter(Role.name == r_name))
            role = res.scalars().first()
            if not role:
                role = Role(name=r_name, description=f"{r_name.capitalize()} role")
                session.add(role)
                await session.flush()
                logger.info(f"Created Role: {r_name}")
            roles_dict[r_name] = role

        # 2. Create Admin User
        res = await session.execute(select(User).filter(User.email == "admin@amazon.com"))
        admin = res.scalars().first()
        if not admin:
            admin = User(
                email="admin@amazon.com",
                hashed_password=hash_password("Admin@123456"),
                full_name="Amazon Admin User",
                phone_number="+1-800-555-0199",
                is_active=True,
                is_verified=True
            )
            session.add(admin)
            await session.flush()
            
            mapping = UserRoleMap(user_id=admin.id, role_id=roles_dict["admin"].id)
            session.add(mapping)
            await session.flush()
            logger.info("Created Admin User: admin@amazon.com / Admin@123456")

        # 3. Create Sample Warehouse
        res = await session.execute(select(Warehouse).filter(Warehouse.code == "WH-US-01"))
        warehouse = res.scalars().first()
        if not warehouse:
            warehouse = Warehouse(
                name="Seattle Primary Logistics Center",
                code="WH-US-01",
                location="Seattle, WA, USA",
                capacity=500000
            )
            session.add(warehouse)
            await session.flush()
            logger.info("Created Warehouse: WH-US-01")

        # 4. Create Categories
        categories_data = [
            {"name": "Electronics", "slug": "electronics", "description": "Gadgets, Devices and Audio"},
            {"name": "Laptops & Computers", "slug": "laptops-computers", "description": "High performance computing"},
            {"name": "Fashion & Apparel", "slug": "fashion-apparel", "description": "Clothing, Shoes & Accessories"}
        ]
        cat_dict = {}
        for cdata in categories_data:
            res = await session.execute(select(Category).filter(Category.slug == cdata["slug"]))
            cat = res.scalars().first()
            if not cat:
                cat = Category(name=cdata["name"], slug=cdata["slug"], description=cdata["description"])
                session.add(cat)
                await session.flush()
                logger.info(f"Created Category: {cdata['name']}")
            cat_dict[cdata["slug"]] = cat

        # 5. Create Products & Inventories
        products_data = [
            {
                "sku": "AMZ-IPHONE-15-PRO",
                "title": "Apple iPhone 15 Pro Max 256GB Titanium",
                "slug": "apple-iphone-15-pro-max",
                "description": "A17 Pro chip, Titanium design, 48MP camera system, Action Button.",
                "brand": "Apple",
                "price": 1199.00,
                "discount_percentage": 5.0,
                "category": cat_dict.get("electronics"),
                "stock": 150
            },
            {
                "sku": "AMZ-SONY-WH1000XM5",
                "title": "Sony WH-1000XM5 Wireless Noise Canceling Headphones",
                "slug": "sony-wh1000xm5-headphones",
                "description": "Industry leading noise cancellation, crystal clear hands-free calling.",
                "brand": "Sony",
                "price": 399.99,
                "discount_percentage": 10.0,
                "category": cat_dict.get("electronics"),
                "stock": 80
            },
            {
                "sku": "AMZ-DELL-XPS-15",
                "title": "Dell XPS 15 Laptop Intel i9 32GB RAM 1TB SSD",
                "slug": "dell-xps-15-laptop",
                "description": "15.6 inch 3.5K OLED touch display, NVIDIA GeForce RTX 4060.",
                "brand": "Dell",
                "price": 2299.00,
                "discount_percentage": 8.0,
                "category": cat_dict.get("laptops-computers"),
                "stock": 45
            }
        ]

        search_repo = SearchRepository()
        for pdata in products_data:
            res = await session.execute(select(Product).filter(Product.sku == pdata["sku"]))
            prod = res.scalars().first()
            if not prod:
                prod = Product(
                    sku=pdata["sku"],
                    title=pdata["title"],
                    slug=pdata["slug"],
                    description=pdata["description"],
                    brand=pdata["brand"],
                    price=pdata["price"],
                    discount_percentage=pdata["discount_percentage"],
                    category_id=pdata["category"].id if pdata["category"] else None
                )
                session.add(prod)
                await session.flush()

                inv = Inventory(
                    product_id=prod.id,
                    warehouse_id=warehouse.id,
                    quantity=pdata["stock"],
                    low_stock_threshold=10
                )
                session.add(inv)
                await session.flush()

                search_repo.index_product(
                    prod.id,
                    prod.title,
                    prod.description,
                    prod.brand,
                    pdata["category"].name if pdata["category"] else ""
                )
                logger.info(f"Created Product: {pdata['title']}")

        await session.commit()
        logger.info("Database seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
