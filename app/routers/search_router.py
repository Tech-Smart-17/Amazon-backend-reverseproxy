"""
Semantic Search & Autocomplete Endpoints (/api/v1/search).
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from app.services.search_service import SearchService
from app.dependencies import get_search_service

router = APIRouter(prefix="/search", tags=["Search Engine"])

@router.get("")
async def search_products(
    q: str = Query(..., min_length=1, description="Search query string"),
    limit: int = Query(10, ge=1, le=50),
    search_service: SearchService = Depends(get_search_service)
):
    """Hybrid Semantic & Keyword search leveraging ChromaDB vector store."""
    return await search_service.search_products(query=q, limit=limit)

@router.get("/autocomplete")
async def autocomplete(
    prefix: str = Query(..., min_length=1),
    search_service: SearchService = Depends(get_search_service)
):
    """Instant query auto-completion."""
    return await search_service.autocomplete(prefix=prefix)

@router.get("/trending")
async def trending_products(search_service: SearchService = Depends(get_search_service)):
    """Fetch currently popular and trending items."""
    return await search_service.get_trending_products()
