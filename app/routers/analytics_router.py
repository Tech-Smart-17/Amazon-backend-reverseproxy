"""
Analytics Dashboard Endpoints (/api/v1/analytics).
"""
from fastapi import APIRouter, Depends
from app.schemas.all_schemas import AnalyticsDashboardResponse
from app.services.analytics_service import AnalyticsService
from app.dependencies import get_analytics_service, require_roles
from app.models.sql_models import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/dashboard", response_model=AnalyticsDashboardResponse)
async def get_dashboard_metrics(
    current_user: User = Depends(require_roles(["admin", "manager"])),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    return await analytics_service.get_dashboard_metrics()
