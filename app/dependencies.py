"""
FastAPI dependency injection providers for Database sessions, Authentication, and Services.
"""
from typing import AsyncGenerator, Callable, List
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.security import decode_token
from app.repositories.user_repository import UserRepository
from app.models.sql_models import User
from app.exceptions import UnauthorizedError, ForbiddenError
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.product_service import ProductService
from app.services.search_service import SearchService
from app.services.cart_service import CartService
from app.services.wishlist_service import WishlistService
from app.services.order_service import OrderService
from app.services.payment_service import PaymentService
from app.services.invoice_service import InvoiceService
from app.services.recommendation_service import RecommendationService
from app.services.notification_service import NotificationService
from app.services.analytics_service import AnalyticsService, AdminService
from app.services.knowledge_service import KnowledgeService
from app.services.sql_agent_service import SQLAgentService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Extract and validate JWT token to get current authenticated user."""
    payload = decode_token(token)
    user_id: str = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Invalid token payload")
    
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise UnauthorizedError("User inactive or not found")
    return user

def require_roles(allowed_roles: List[str]):
    """Role-Based Access Control (RBAC) dependency factory."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_roles = [r.name for r in current_user.roles]
        # Superadmin override or direct role match
        if "admin" in user_roles or any(r in user_roles for r in allowed_roles):
            return current_user
        raise ForbiddenError(f"Access forbidden. Requires one of roles: {allowed_roles}")
    return role_checker

# Service Injectors
def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    return ProductService(db)

def get_search_service(db: AsyncSession = Depends(get_db)) -> SearchService:
    return SearchService(db)

def get_cart_service(db: AsyncSession = Depends(get_db)) -> CartService:
    return CartService(db)

def get_wishlist_service(db: AsyncSession = Depends(get_db)) -> WishlistService:
    return WishlistService(db)

def get_order_service(db: AsyncSession = Depends(get_db)) -> OrderService:
    return OrderService(db)

def get_payment_service(db: AsyncSession = Depends(get_db)) -> PaymentService:
    return PaymentService(db)

def get_invoice_service(db: AsyncSession = Depends(get_db)) -> InvoiceService:
    return InvoiceService(db)

def get_recommendation_service(db: AsyncSession = Depends(get_db)) -> RecommendationService:
    return RecommendationService(db)

def get_notification_service() -> NotificationService:
    return NotificationService()

def get_analytics_service(db: AsyncSession = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)

def get_admin_service(db: AsyncSession = Depends(get_db)) -> AdminService:
    return AdminService(db)

def get_knowledge_service() -> KnowledgeService:
    return KnowledgeService()

def get_sql_agent_service() -> SQLAgentService:
    return SQLAgentService()
