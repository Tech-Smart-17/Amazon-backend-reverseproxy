"""
Vector Recommendation Engine Endpoints (/api/v1/recommendations).
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from app.services.recommendation_service import RecommendationService
from app.dependencies import get_recommendation_service

router = APIRouter(prefix="/recommendations", tags=["Recommendation Engine"])

@router.get("/similar/{product_id}")
async def get_similar_products(
    product_id: str,
    limit: int = Query(5, ge=1, le=20),
    rec_service: RecommendationService = Depends(get_recommendation_service)
):
    """Fetch vector-similar product recommendations from ChromaDB."""
    return await rec_service.get_similar_products(product_id, limit)

@router.get("/frequently-bought/{product_id}")
async def get_frequently_bought_together(
    product_id: str,
    rec_service: RecommendationService = Depends(get_recommendation_service)
):
    """Fetch complementary products commonly purchased together."""
    return await rec_service.get_frequently_bought_together(product_id)
