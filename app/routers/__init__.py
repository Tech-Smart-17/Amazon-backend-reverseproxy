"""
Routers package exports.
"""
from app.routers.auth_router import router as auth_router
from app.routers.users_router import router as users_router
from app.routers.products_router import router as products_router
from app.routers.categories_router import router as categories_router
from app.routers.search_router import router as search_router
from app.routers.inventory_router import router as inventory_router
from app.routers.warehouse_router import router as warehouse_router
from app.routers.cart_router import router as cart_router
from app.routers.wishlist_router import router as wishlist_router
from app.routers.address_router import router as address_router
from app.routers.orders_router import router as orders_router
from app.routers.payments_router import router as payments_router
from app.routers.invoices_router import router as invoices_router
from app.routers.notifications_router import router as notifications_router
from app.routers.recommendations_router import router as recommendations_router
from app.routers.analytics_router import router as analytics_router
from app.routers.admin_router import router as admin_router
from app.routers.ai_router import router as ai_router
from app.routers.voice_router import router as voice_router

__all__ = [
    "auth_router", "users_router", "products_router", "categories_router",
    "search_router", "inventory_router", "warehouse_router", "cart_router",
    "wishlist_router", "address_router", "orders_router", "payments_router",
    "invoices_router", "notifications_router", "recommendations_router",
    "analytics_router", "admin_router", "ai_router", "voice_router"
]
