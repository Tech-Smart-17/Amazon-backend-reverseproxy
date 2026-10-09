"""
Search Service combining ChromaDB vector similarity and SQL database filtering.
"""
from typing import List, Dict, Any
import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.search_repository import SearchRepository
from app.repositories.product_repository import ProductRepository

logger = logging.getLogger("amazon_backend.search")

class SearchService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.search_repo = SearchRepository()
        self.product_repo = ProductRepository(db)

    async def search_products(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Hybrid search combining ChromaDB vector embeddings search
        with SQL keyword search fallback.
        """
        try:
            vector_product_ids = await asyncio.to_thread(
                self.search_repo.search_semantic, query, limit
            )
        except Exception:
            logger.exception("Semantic search failed; using SQL keyword fallback")
            vector_product_ids = []
        
        results = []
        seen_ids = set()
        
        # 1. Fetch ChromaDB matches
        for pid in vector_product_ids:
            p = await self.product_repo.get_by_id(pid)
            if p and p.is_active:
                seen_ids.add(p.id)
                results.append({
                    "id": p.id,
                    "title": p.title,
                    "price": p.price,
                    "brand": p.brand,
                    "search_type": "semantic_vector"
                })

        # 2. SQL keyword fallback if vector search returned few items
        if len(results) < limit:
            sql_products = await self.product_repo.filter_products(search_query=query, limit=limit)
            for p in sql_products:
                if p.id not in seen_ids:
                    seen_ids.add(p.id)
                    results.append({
                        "id": p.id,
                        "title": p.title,
                        "price": p.price,
                        "brand": p.brand,
                        "search_type": "keyword_match"
                    })

        return results[:limit]

    async def autocomplete(self, prefix: str) -> List[str]:
        """Provide autocomplete query suggestions."""
        products = await self.product_repo.filter_products(search_query=prefix, limit=5)
        return [p.title for p in products]

    async def get_trending_products(self) -> List[Dict[str, Any]]:
        """Return popular/trending catalog products."""
        products = await self.product_repo.filter_products(limit=5)
        return [{"id": p.id, "title": p.title, "price": p.price} for p in products]
